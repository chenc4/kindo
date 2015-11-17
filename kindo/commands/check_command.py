#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.api import cd
from fabric.contrib.files import exists
from fabric.context_managers import shell_env
from kindo.commands.command import Command


class CheckCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value):
        if not value[6:]:
            return {}

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

    def run(self, command, filesdir, imagesdir, position, envs):
        with cd(position):
            with shell_env(**envs):
                for port in command["args"]["ports"]:
                    stdout = self.execute("netstat –apn | grep %s" % port)
                    if not stdout.strip():
                        return 0, position, "CHECK ERROR: %s not found" % port, envs

                for f in command["args"]["files"]:
                    if not exists(f):
                        return 0, position, "CHECK ERROR: %s not found" % f, envs

                return position, envs
        return position, envs
