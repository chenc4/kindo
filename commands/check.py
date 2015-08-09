#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.api import cd
from fabric.contrib.files import exists
from commands.command import Command


class Check(Command):
    def __init__(self):
        Command.__init__(self)

    def parse(self, value):
        value = value.strip()
        if len(value) > 6 and value[:6].lower() == "check ":
            strs = re.split("\s+", value[6:])

            ports = []
            files = []

            for s in strs:
                if s.isdigit():
                    ports.append(s)
                else:
                    files.append(s)

            return {
                "action": "CHECK",
                "args": {"ports": ports, "files": files},
                "variables": []
            }
        return {}

    def run(self, command, deps_folder, position=None):
        if "action" not in command:
            return False

        if command["action"] != "CHECK":
            return False

        with cd(position):
            self.position = position

            for port in command["args"]["ports"]:
                stdout = self.execute("netstat –apn | grep %s" % port)
                if not stdout.strip():
                    raise Exception("%s not existed" % port)

            for f in command["args"]["files"]:
                if not exists(f):
                    raise Exception("%s not existed" % f)
        return True
