#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import stat
import paramiko


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
        self.shell = "/bin/bash -l -c"

    def execute(self, command, cd=None, envs=None, sudo=False, user=None, group=None, shell=None):
        try:
            command = self._cd_wrap(command, cd)
            command = self._env_wrap(command, envs)
            command = self._shell_wrap(command)
            if sudo:
                command = self._sudo_wrap(command, self.username if user is None else user, group)
            # if sudo, must use pty. "sudo: sorry, you must have a tty to run sudo"
            stdin, stdout, stderr = self.ssh_client.exec_command(command, get_pty=True if sudo else False)
            return [line.strip() for line in stdout.readlines()], [line.strip() for line in stderr.readlines()]
        except:
            return [], []

    def sudo(self, command, cd=None, envs=None):
        return self.execute(command, cd, envs, True)

    def put(self, local, remote):
        files = []

        try:
            if remote[-1] == "/":
                remote = remote[:-1]

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
                self.sftp.put(local, remote)
                files.append(remote)
        except:
            pass
        return files

    def get(self, remote, local, overwrite=True, topdown=True):
        files = []
        try:
            if remote is None or local is None:
                return files

            if not remote or not local:
                return files

            remote_is_dir = self.isdir(remote)
            if os.path.isdir(local) and not remote_is_dir:
                return files

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

                    self.sftp.get(src, target)
                    files.append(target)
        except:
            pass

        return files

    def shell(self):
        pass

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

    def exists(self, path):
        try:
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

        return '{} "{}"'.format(self.shell if shell is None else shell, command)

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

        return 'sudo -S -p "{}" {}'.format(self.sudo_prompt, command)

    def _cd_wrap(self, command, cd=None):
        if cd is None:
            return command
        return 'cd "{}" && {}'.format(cd, command)

    def _env_wrap(self, command, envs=None):
        if envs is None:
            return command

        exports = ' '.join(
            '%s="%s"' % (k, v if k == 'PATH' else self._shell_escape(v))
            for k, v in list(envs.items())
        )

        return 'export {} && {}'.format(exports, command)


if __name__ == "__main__":
    client = KiSSHClient("172.16.79.22", 12302, "root", "iflytek!@#2014")
    print(client.execute("echo 123 && pwd", "/usr/local"))
    client.mkdir("/test", True)
    print(client.isdir("/test"))
    print(client.exists("/test"))
    print(client.isdir("/test/1"))
    print(client.islink("/test"))
    print(client.put("D:/1 2", "/test/"))
    print(client.get("/test/", "D:/text"))
