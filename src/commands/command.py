#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import requests
from fabric.contrib.files import exists
from fabric.api import env, sudo, settings, run, hide, put, get


class Command:
    def __init__(self):
        self._has_sudo = None
        self._system_info = None
        self.deps = []

    def get_deps(self):
        return self.deps

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
        if not os.path.isfile(filepath):
            return False

        if os.path.isfile(filepath):
            if target[-1] == "/":
                folder = target
            else:
                folder = os.path.dirname(target)

            if not exists(folder, use_sudo=self.has_sudo()):
                self.execute("mkdir -p %s" % folder)

            put(filepath, target, use_sudo=self.has_sudo())

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
        return False

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

                self._system_info = {
                    "kernel": self.execute("uname -a"),
                    "system": self.execute("cat /etc/issue"),
                    "bit": int(self.execute("getconf LONG_BIT")),
                    "memery": {
                        "total": int(memery_stdouts[1]),
                        "used": int(memery_stdouts[2]),
                        "free": int(memery_stdouts[3]),
                        "shared": int(memery_stdouts[4]),
                        "buffers": int(memery_stdouts[5]),
                        "cached": int(memery_stdouts[6])
                    },
                    "disk": {
                        "total": disk_stdouts[1],
                        "used": disk_stdouts[2],
                        "avail": disk_stdouts[3]
                    }
                }
        return self._system_info
