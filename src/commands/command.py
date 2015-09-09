#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import requests
from fabric.contrib.files import exists
from fabric.api import env, sudo, settings, run, hide, put, get
from utils.configParser import ConfigParser


class Command:
    def __init__(self, startfolder, configs, options, logger):
        self.startfolder = startfolder
        self.configs = configs
        self.options = options
        self.logger = logger

        self._has_sudo = None
        self._system_info = None
        self.deps = []

        self.kindo_settings_path = os.getenv("KINDO_SETTINGS_PATH")

        if self.kindo_settings_path is None:
            settings_path = os.path.join(self.startfolder, "settings")
            if not os.path.isdir(settings_path):
                if os.getenv("APPDATA") is None:
                    if os.path.isdir("/etc/opt"):
                        self.kindo_settings_path = "/etc/opt/kindo"
                    else:
                        self.kindo_settings_path = os.path.join(self.kindo_tmps_path, "settings")
                else:
                    self.kindo_settings_path = os.path.join(os.getenv("APPDATA"), "kindo", "settings")
            else:
                self.kindo_settings_path = settings_path

        self.configs = dict(self.get_kindo_setting(), **self.configs)

    def get_kindo_setting(self):
        ini_path = os.path.join(self.kindo_settings_path, "kindo.ini")
        if not os.path.isfile(ini_path):
            return {}

        cf = ConfigParser()
        cf.read(ini_path)

        configs = {}
        for section in cf.sections():
            items = cf.items(section)
            section = section.lower()

            for k, v in items:
                k = k.strip()
                v = v.strip()
                configs[k] = v
        return configs

    def has_sudo(self):
        if self._has_sudo is None:
            self._has_sudo = False
            with settings(hide('stderr', 'warnings'), warn_only=True):
                sudo("echo")
                self._has_sudo = True
        return self._has_sudo

    def execute(self, cmd):
        if self.has_sudo():
            return sudo(cmd)
        return run(cmd)

    def clean(self):
        for dep in self.deps:
            try:
                self.execute("rm -rf %s" % dep)
            except:
                pass

    def upload(self, filepath, target, unzip=False):
        if not os.path.isfile(filepath) and not os.path.isdir(filepath):
            return False

        if target[-1] == "/":
            folder = target
        else:
            folder = os.path.dirname(target)

        if not exists(folder, use_sudo=self.has_sudo()):
            self.execute("mkdir -p %s" % folder)

        put(filepath, target, use_sudo=self.has_sudo())

        if os.path.isfile(filepath):
            if exists(target, use_sudo=self.has_sudo()):
                if unzip:
                    name, ext = os.path.splitext(target)
                    if ext.lower() == ".tar.gz":
                        self.execute("tar -xzvf %s && rm -f %s" % (target, target))
                    elif ext.lower() == ".tar.gz2":
                        self.execute("tar -czvf %s && rm -f %s" % (target, target))
                    elif ext.lower() == ".tar":
                        self.execute("tar -xvf %s && rm -f %s" % (target, target))
                    elif ext.lower() == ".zip":
                        self.execute("unzip %s && rm -f %s" % (target, target))
        return True

    def download(self, remote, local):
        if exists(remote, use_sudo=self.has_sudo()):
            if local[-1] == "/":
                folder = local
            else:
                folder = os.path.dirname(local)

            if not os.path.isdir(folder):
                os.makedirs(folder)

            get(remote, local)
            return True
        return False

    def download_by_url(self, url, local):
        r = requests.get(url)
        if r.status_code == 200:
            if local[-1] == "/":
                folder = local
            else:
                folder = os.path.dirname(local)

            if not os.path.isdir(folder):
                os.makedirs(folder)

            if local[-1] == "/":
                target = os.path.join(local, os.path.split(url)[1])
            else:
                target = local
            with open(target, "wb") as fs:
                fs.write(r.content)

            return True
        return False

    def get_system_info(self):
        if self._system_info is None:
            with settings(hide('stderr', 'warnings'), warn_only=True):
                memery_stdouts = [v for v in self.execute("free -l|sed -n '2,2p' |awk '{print $0}'").split(" ") if v != ""]
                disk_stdouts = [v for v in self.execute("df -hl|sed -n '2,2p' |awk '{print $0}'").split(" ") if v != ""]

                bit = 64
                try:
                    bit = int(self.execute("getconf LONG_BIT"))
                except:
                    pass

                self._system_info = {
                    "kernel": self.execute("uname -a"),
                    "system": self.execute("cat /etc/issue"),
                    "bit": bit,
                    "memery": {
                        "total": int(memery_stdouts[1]) if len(memery_stdouts) > 2 else -1,
                        "used": int(memery_stdouts[2]) if len(memery_stdouts) > 3 else -1,
                        "free": int(memery_stdouts[3]) if len(memery_stdouts) > 4 else -1,
                        "shared": int(memery_stdouts[4]) if len(memery_stdouts) > 5 else -1,
                        "buffers": int(memery_stdouts[5]) if len(memery_stdouts) > 6 else -1,
                        "cached": int(memery_stdouts[6]) if len(memery_stdouts) > 7 else -1
                    },
                    "disk": {
                        "total": disk_stdouts[1] if len(disk_stdouts) > 2 else -1,
                        "used": disk_stdouts[2] if len(disk_stdouts) > 3 else -1,
                        "avail": disk_stdouts[3] if len(disk_stdouts) > 4 else -1
                    }
                }
        return self._system_info
