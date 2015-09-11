#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import requests
from fabric.contrib.files import exists
from fabric.api import env, sudo, settings, run, hide, put, get
from utils.configParser import ConfigParser
from core.kindoCore import KindoCore


class Command(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

        self._has_sudo = None
        self._system_info = None

    def has_sudo(self):
        if self._has_sudo is None:
            self._has_sudo = False
            with settings(hide('stderr', 'warnings'), warn_only=True):
                sudo("echo", user=env.user)
                self._has_sudo = True
        return self._has_sudo

    def execute(self, cmd):
        if self.has_sudo():
            return sudo(cmd, user=env.user)
        return run(cmd)

    def upload(self, filepath, target, target_is_dir=None):
        if not os.path.isfile(filepath) and not os.path.isdir(filepath):
            self.logger.debug("no found: %s" % filepath)
            return False

        if target_is_dir is None:
            if os.path.isdir(filepath):
                if not exists(target, use_sudo=self.has_sudo()):
                    self.execute("mkdir -p %s" % target)
            elif os.path.isfile(filepath):
                if target[-1] == "/" and not exists(target, use_sudo=self.has_sudo()):
                    self.execute("mkdir -p %s" % target)
        elif target_is_dir:
            if not exists(target, use_sudo=self.has_sudo()):
                self.execute("mkdir -p %s" % target)

        with settings(hide('stderr', 'warnings'), warn_only=True):
            self.logger.debug("putting %s" % filepath)
            put(filepath, target, use_sudo=self.has_sudo())
            self.logger.debug("putted %s" % filepath)
            return True
        return False

    def download(self, remote, local):
        if exists(remote, use_sudo=self.has_sudo()):
            if target[-1] == "/" and not os.path.isdir(local):
                os.makedirs(local)

            with settings(hide('stderr', 'warnings'), warn_only=True):
                get(remote, local, use_sudo=self.has_sudo())
                return True
        return False

    def download_by_url(self, url, local):
        r = requests.get(url)
        if r.status_code == 200:
            if local[-1] == "/" and not os.path.isdir(local):
                os.makedirs(local)

            target = local
            if local[-1] == "/":
                target = os.path.join(local, os.path.split(url)[1])

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
