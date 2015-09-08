#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.api import cd
from fabric.contrib.files import exists
from commands.command import Command


class CheckCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

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
            return -1, position, ""

        if command["action"] != "CHECK":
            return -1, position, ""

        with cd(position):
            for port in command["args"]["ports"]:
                stdout = self.execute("netstat –apn | grep %s" % port)
                if not stdout.strip():
                    return 0, position, "CHECK ERROR: %s not found" % port

            for f in command["args"]["files"]:
                if not exists(f):
                    return 0, position, "CHECK ERROR: %s not found" % f

            return 1, position, ""
        return 1, position, ""
