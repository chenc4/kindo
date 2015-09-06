#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import shutil
import traceback
import zipfile
import pickle
import simplejson
from fabric.state import output
from fabric.tasks import execute
from fabric.api import env
from modules.kindoModule import KindoModule
from utils.configParser import ConfigParser
from commands.addCommand import AddCommand
from commands.checkCommand import CheckCommand
from commands.runCommand import RunCommand
from commands.workdirCommand import WorkdirCommand
from commands.downloadCommand import DownloadCommand
from commands.ubuntuCommand import UbuntuCommand
from commands.centosCommand import CentOSCommand


class RunModule(KindoModule):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoModule.__init__(self, command, startfolder, configs, options, logger)

        env.colorize_errors = True
        env.command_timeout = 60 * 30
        env.output_prefix = ""
        env.passwords = {}
        output.debug = False
        output.running = False

        host = configs.get("h", None)
        host = "%s:22" % host if host is not None and host.rfind(":") == -1 else host
        host = "root@%s" % host if host is not None and host.rfind("@") == -1 else host

        password = configs.get("p", "")

        if host is not None:
            env.passwords[host] = password

        hosts = self.get_hosts_setting()

        groups = configs["g"].split(",") if "g" in configs else []
        for group in groups:
            group = group.strip()

            if group not in hosts:
                self.logger.warn("GROUP NOT FOUND: %s" % group)
                continue

            for k, v in hosts[group].items():
                env.passwords[k] = v

        if len(env.passwords) == 0 and "default" in hosts:
            for k, v in hosts["default"].items():
                env.passwords[k] = v

        self.ki_path = self.get_ki_path()

        self.handlers = {
            "add": AddCommand(),
            "check": CheckCommand(),
            "run": RunCommand(),
            "workdir": WorkdirCommand(),
            "download": DownloadCommand(),
            "ubuntu": UbuntuCommand(),
            "centos": CentOSCommand()
        }

    def start(self):
        if not os.path.isfile(self.ki_path):
            self.logger.error("KI NOT FOUND: %s" % self.ki_path)
            return

        if env.passwords is None or len(env.passwords) == 0:
            self.logger.error("ARGS ERROR: hosts not found")
            return

        dirname, filename = os.path.split(self.ki_path)
        cache_folder, length = self.get_cache_info(filename)
        if (
            length != os.path.getsize(self.ki_path) or
            not os.path.isdir(cache_folder)
        ):
            if not self.unzip_file(self.ki_path, cache_folder):
                self.logger.error("UNPACKAGE ERROR")
                return

        ki_kibcs_path = os.path.join(cache_folder, "kibcs")
        ki_files_path = os.path.join(cache_folder, "files")

        # 兼容老版本的安装包
        if not os.path.isdir(ki_kibcs_path):
            ki_kibcs_path = os.path.join(cache_folder, "confs")

        if not os.path.isdir(ki_files_path):
            ki_files_path = os.path.join(cache_folder, "deps")

        if not os.path.isdir(ki_kibcs_path):
            self.logger.error("INVALID KI PACKAGE")
            return

        for f in os.listdir(ki_kibcs_path):
            filename, ext = os.path.splitext(f)
            if ext != ".kibc":
                continue

            script = os.path.join(ki_kibcs_path, f)
            with open(script, 'rb') as fs:
                try:
                    script_commands = pickle.load(fs)

                    execute(
                        self.execute_script_commands,
                        commands=script_commands,
                        files_folder=ki_files_path,
                        hosts=env.passwords.keys()
                    )
                except:
                    self.logger.debug(traceback.format_exc())
                    self.logger.error("EXECUTE ERROR")

    def execute_script_commands(self, commands, files_folder):
        position = "~"
        for command in commands:
            if "action" not in command:
                self.logger.error("KI RUN ERROR: command invalid")
                return

            action = command["action"].lower()
            if action not in self.handlers:
                self.logger.error("KI RUN ERROR: %s not supported" % action)
                return

            status, position, errormsg = self.handlers[action].run(command, files_folder, position)
            # if the command is executed(success or fail), not continue
            if status == 0:
                self.logger.error(errormsg)

    def get_ki_path(self):
        ki_path = self.options[0] if len(self.options) == 1 else self.options[1]
        if ki_path[-3:] != ".ki":
            ki_path = "%s.ki" % ki_path

        if not os.path.isfile(ki_path):
           path = os.path.realpath(ki_path)
           if not os.path.isfile(path):
                path = os.path.join(self.startfolder, "packages", ki_path)
                if not os.path.isfile(path):
                    path = os.path.join(self.startfolder, ki_path)
                    if not os.path.isfile(path):
                        path = os.path.join(self.kindo_packages_path, ki_path)
                        if not os.path.isfile(path):
                            # for example: /var/opt/kindo/packages/nginx/nginx-1.0.0/nginx-1.0.0.ki
                            whole_name, ext = os.path.splitext(ki_path)
                            last_hyphen_pos = whole_name.rfind("-")
                            name = whole_name if last_hyphen_pos == -1 else whole_name[:last_hyphen_pos]
                            path = os.path.join(self.kindo_packages_path, name, whole_name, ki_path)

                if os.path.isfile(path):
                    ki_path = path

        return ki_path

    def get_cache_info(self, filename):
        # for example: /var/cache/kindo/nginx/nginx-1.0.0
        whole_name, ext = os.path.splitext(filename)
        last_hyphen_pos = whole_name.rfind("-")
        name = whole_name if last_hyphen_pos == -1 else whole_name[:last_hyphen_pos]

        cache_folder = os.path.join(self.kindo_caches_path, name, whole_name)
        cache_file = os.path.join(cache_folder, "ki.cache")
        if not os.path.isfile(cache_file):
            return cache_folder, 0

        with open(cache_file, "r") as fs:
            try:
                return cache_folder, int(fs.read())
            except:
                return cache_folder, 0

    def unzip_file(self, zipfilename, unziptodir):
        try:
            if not os.path.exists(unziptodir):
                os.makedirs(unziptodir)

            zfobj = zipfile.ZipFile(zipfilename)

            if "kipwd" in self.configs and self.configs["kipwd"]:
                zfobj.setpassword(self.configs["kipwd"])

            for name in zfobj.namelist():
                name = name.replace('\\','/')

                if name.endswith('/'):
                    os.makedirs(os.path.join(unziptodir, name))
                else:
                    ext_filename = os.path.join(unziptodir, name)
                    ext_dir= os.path.dirname(ext_filename)
                    if not os.path.exists(ext_dir):
                        os.makedirs(ext_dir)

                    with open(ext_filename, 'wb') as fs:
                        fs.write(zfobj.read(name))

            return True
        except Exception as e:
            self.logger.debug(traceback.format_exc())
        return False

    def get_hosts_setting(self):
        ini_path = os.path.join(self.kindo_settings_path, "hosts.ini")
        if not os.path.isfile(ini_path):
            return {}

        cf = ConfigParser()
        cf.read(ini_path)

        hosts = {}
        for section in cf.sections():
            items = cf.items(section)
            section = section.lower()

            hosts[section] = {}
            for host, password in items:
                host = host.strip()
                password = password.strip()

                host = "%s:22" % host if host is not None and host.rfind(":") == -1 else host
                host = "root@%s" % host if host is not None and host.rfind("@") == -1 else host

                hosts[section][host] = password
        return hosts


