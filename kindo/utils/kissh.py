#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import stat
import time
import traceback
import threading
import paramiko
from select import select

win32 = (sys.platform == 'win32')

if win32:
    import msvcrt
    import ctypes

    STD_OUTPUT_HANDLE = -11
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    def set_color(color, handle=std_out_handle):
        bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return bool
else:
    def std_out_handle():
        pass

    def set_color(color, handle=std_out_handle):
        pass

FOREGROUND_WHITE = 0x0007
FOREGROUND_BLUE = 0x01  # text color contains blue.
FOREGROUND_GREEN = 0x02  # text color contains green.
FOREGROUND_RED = 0x04  # text color contains red.
FOREGROUND_YELLOW = FOREGROUND_RED | FOREGROUND_GREEN


def output_loop(*args, **kwargs):
    OutputLooper(*args, **kwargs).loop()


def input_loop(chan, using_pty):
    while not chan.exit_status_ready():
        if win32:
            have_char = msvcrt.kbhit()
        else:
            r, w, x = select([sys.stdin], [], [], 0.0)
            have_char = (r and r[0] == sys.stdin)
        if have_char and chan.input_enabled:
            # Send all local stdin to remote end's stdin
            byte = msvcrt.getch() if win32 else sys.stdin.read(1)
            chan.sendall(byte)
            # Optionally echo locally, if needed.
            if not using_pty:
                # Not using fastprint() here -- it prints as 'user'
                # output level, don't want it to be accidentally hidden
                sys.stdout.write(byte)
                sys.stdout.flush()
        time.sleep(paramiko.io_sleep)


class OutputLooper(object):
    def __init__(self, chan, attr, stream, capture, timeout, printing=True):
        self.chan = chan
        self.stream = stream
        self.capture = capture
        self.timeout = timeout
        self.stdout_error = True if attr == "recv_stderr" else False
        self.read_func = getattr(chan, attr)

        self.printing = printing
        self.read_size = 10
        self.write_buffer = ""

    def _flush(self, text=None):
        if text is None:
            self.capture.extend(self.write_buffer.split("\n")[:-1])
            return

        if text:
            if self.stdout_error:
                set_color(FOREGROUND_RED)
            self.stream.write(text)

            if text[-1] in ["\n", "\r", ".", u"。", " "]:
                self.stream.flush()
            if self.stdout_error:
                set_color(FOREGROUND_WHITE)
            self.write_buffer += text.strip("\r")

    def loop(self):
        try:
            while True:
                bytelist = self.read_func(self.read_size)
                if not bytelist:
                    self._flush()
                    break

                self._flush(bytelist.decode("utf-8"))
        except:
            print(traceback.format_exc())


class ThreadHandler(object):
    def __init__(self, name, callable, *args, **kwargs):
        # Set up exception handling
        self.exception = None

        def wrapper(*args, **kwargs):
            try:
                callable(*args, **kwargs)
            except BaseException:
                self.exception = sys.exc_info()
        # Kick off thread
        thread = threading.Thread(None, wrapper, name, args, kwargs)
        thread.setDaemon(True)
        thread.start()
        # Make thread available to instantiator
        self.thread = thread

    def raise_if_needed(self):
        if self.exception:
            e = self.exception
            raise Exception(e)


class KiSSHClient:
    def __init__(self, hostname, port=22, username=None, key=None):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.key = key

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.hostname, self.port, self.username, self.key)
        self.sftp = self.ssh_client.open_sftp()

        self.sudo_prompt = "sudo password:"
        self._shell = "/bin/bash -l -c"
        self.has_sudo = None
        self.execute_timeout = 60 * 3

    def execute(self, command, cd=None, envs=None, sudo=False, user=None, group=None, shell=False):
        try:
            if cd is not None and cd[-1] == "/":
                cd = cd[:-1]

            if cd is not None and cd.startswith("~"):
                home = self.sftp.normalize('.')
                cd = cd.replace('~', home, 1)

            command = self._cd_wrap(command, cd)
            command = self._env_wrap(command, envs)
            command = self._shell_wrap(command)
            if sudo:
                command = self._sudo_wrap(command, self.username if user is None else user, group)
            # if sudo, must use pty. "sudo: sorry, you must have a tty to run sudo"
            return self.exec_command(command, get_pty=sudo)
        except Exception as e:
            return [], [str(e)]

    def sudo(self, command, cd=None, envs=None):
        if self.has_sudo is None:
            stdouts, stderrs, status = self.execute("sudo echo test", sudo=True)
            self.has_sudo = True if status == 0 else False

        return self.execute(command, cd, envs, self.has_sudo)

    def put(self, local, remote, cd=None):
        files = []

        try:
            home = self.sftp.normalize('.')

            if remote[-1] == "/":
                remote = remote[:-1]

            if remote.startswith('~'):
                remote = remote.replace('~', home, 1)

            if cd is not None and cd[-1] == "/":
                cd = cd[:-1]

            if cd is not None and cd.startswith("~"):
                cd = cd.replace('~', home, 1)

            if not os.path.isabs(remote) and cd is not None:
                remote = '{}/{}'.format(cd, remote)

            if os.path.isdir(local):
                if self.exists(remote) and not self.isdir(remote):
                    return files

            if os.path.isfile(local) and self.isdir(remote):
                return files

            if os.path.isdir(local):
                for f in os.listdir(local):
                    src = os.path.join(local, f)
                    if os.path.isdir(src):
                        target = "{}/{}".format(remote, f)
                        files.extend(self.put(src, target))
                    elif os.path.isfile(src):
                        target = "{}/{}".format(remote, f)

                        if self.islink(remote):
                            continue

                        if not self.exists(remote):
                            self.mkdir(remote)

                        self.sftp.put(src, target)

                        files.append(src)
            elif os.path.isfile(local):
                remote_folder = os.path.dirname(remote)
                if not self.exists(remote_folder):
                    self.mkdir(remote_folder)

                if self.isdir(remote_folder):
                    self.sftp.put(local, remote)
                    files.append(remote)
        except Exception as e:
            print(e)
        return files

    def get(self, remote, local, overwrite=True, topdown=True, cd=None):
        files = []
        try:
            if remote is None or local is None:
                return files

            if not remote or not local:
                return files

            home = self.sftp.normalize('.')

            if remote.startswith('~'):
                remote = remote.replace('~', home, 1)

            if cd is not None and cd[-1] == "/":
                cd = cd[:-1]

            if cd is not None and cd.startswith("~"):
                cd = cd.replace('~', home, 1)

            if not os.path.isabs(remote) and cd is not None:
                remote = '{}/{}'.format(cd, remote)

            remote_is_dir = self.isdir(remote)
            if os.path.isdir(local) and not remote_is_dir:
                folder, filename = os.path.split(remote)
                local = os.path.join(local, filename)

            if not remote_is_dir:
                if not overwrite and os.path.isfile(local):
                    return files

                local_folder = os.path.dirname(local)
                if not os.path.isdir(local_folder):
                    os.makedirs(local_folder)

                self.sftp.get(remote, local)
                files.append(local)
            else:
                if not os.path.isdir(local):
                    os.makedirs(local)

                filenames = self.sftp.listdir(remote)
                for filename in filenames:
                    src = "{}/{}".format(remote, filename)
                    target = os.path.join(local, filename)

                    if topdown and self.isdir(src):
                        files.extend(self.get(src, target, overwrite))
                        continue

                    if not overwrite and os.path.exists(local):
                        continue

                    if self.islink(src):
                        continue

                    target_folder = os.path.dirname(target)
                    if not os.path.isdir(target_folder):
                        os.makedirs(target_folder)

                    if os.path.isdir(target_folder):
                        self.sftp.get(src, target)
                        files.append(target)
        except:
            pass
        return files

    def isdir(self, path):
        try:
            return stat.S_ISDIR(self.sftp.stat(path).st_mode)
        except IOError:
            return False

    def islink(self, path):
        try:
            return stat.S_ISLNK(self.sftp.lstat(path).st_mode)
        except IOError:
            return False

    def exists(self, path, cd=None):
        try:
            home = self.sftp.normalize('.')

            if path.startswith('~'):
                path = path.replace('~', home, 1)

            if cd is not None and cd[-1] == "/":
                cd = cd[:-1]

            if cd is not None and cd.startswith("~"):
                cd = cd.replace('~', home, 1)

            if not os.path.isabs(path) and cd is not None:
                path = '{}/{}'.format(cd, path)

            self.sftp.lstat(path).st_mode
        except IOError:
            return False
        return True

    def mkdir(self, path, sudo=False):
        self.execute('mkdir -p "%s"' % path, sudo=sudo)

    def walk(self, top, topdown=True, followlinks=False):
        try:
            # Note that listdir and error are globals in this module due to
            # earlier import-*.
            names = self.ftp.listdir(top)
        except Exception:
            return []

        dirs, nondirs = [], []
        for name in names:
            if self.isdir(os.path.join(top, name)):
                dirs.append(name)
            else:
                nondirs.append(name)

        if topdown:
            yield top, dirs, nondirs

        for name in dirs:
            path = os.path.join(top, name)
            if followlinks or not self.islink(path):
                for x in self.walk(path, topdown, followlinks):
                    yield x
        if not topdown:
            yield top, dirs, nondirs

    def _shell_escape(self, command):
        for char in ('"', '$', '`'):
            command = command.replace(char, '\%s' % char)
        return command

    def _shell_wrap(self, command, shell=None):
        command = self._shell_escape(command)

        return '{} "{}"'.format(self._shell if shell is None else shell, command)

    def _sudo_wrap(self, command, user, group=None):
        if user is not None and str(user).isdigit():
            user = "#{}".format(user)

        if group is not None and str(group).isdigit():
            group = "#{}".format(group)

        prefix = ""

        if group is not None:
            prefix = '-g "{}"'.format(group)

        if user is not None:
            prefix = '-u "{}" {}'.format(user, prefix)

        return 'sudo -S -p "{}" {} {}'.format(self.sudo_prompt, prefix, command)

    def _cd_wrap(self, command, cd=None):
        if cd is None:
            return command
        return 'cd "{}" && {}'.format(cd, command)

    def _env_wrap(self, command, envs=None):
        if envs is None:
            return command

        exports = []
        for k, v in envs.items():
            if k != 'PATH':
                v = self._shell_escape(v)
            exports.append('%s="%s"' % (k, v))

        return 'export {} && {}'.format(' '.join(exports), command)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        try:
            if self.ssh_client is not None:
                self.ssh_client.close()

            if self.sftp is not None:
                self.sftp.close()
        except:
            pass

    def exec_command(self, command, bufsize=-1, timeout=None, get_pty=False):
        with self.ssh_client._transport.open_session() as channel:
            if get_pty:
                channel.get_pty()
            channel.settimeout(timeout)
            channel.exec_command(command + "\n")

            stdout_buf = []
            stderr_buf = []
            workers = (
                ThreadHandler('out', output_loop, channel, "recv", capture=stdout_buf, stream=sys.stdout, timeout=timeout),
                ThreadHandler('err', output_loop, channel, "recv_stderr", capture=stderr_buf, stream=sys.stderr, timeout=timeout),
                ThreadHandler('in', input_loop, channel, False)
            )

            while True:
                if channel.exit_status_ready():
                    break

                for worker in workers:
                    worker.raise_if_needed()

                try:
                    time.sleep(paramiko.io_sleep)
                except KeyboardInterrupt:
                    channel.send('\x03')

            # Obtain exit code of remote program now that we're done.
            status = channel.recv_exit_status()

            # Wait for threads to exit so we aren't left with stale threads
            for worker in workers:
                worker.thread.join()
                worker.raise_if_needed()

            return stdout_buf, stderr_buf, status
