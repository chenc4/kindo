#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
from kindo.commands.command import Command


class CheckCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value, kic_path=None):
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

    def run(self, ssh_client, command, filesdir, imagesdir, cd, envs, ki_path=None):
        for port in command["args"]["ports"]:
            stdouts, stderrs = ssh_client.execute("netstat –apn | grep %s" % port, cd, envs)
            if len(stderrs) > 0:
                raise Exception("CHECK ERROR: %s not found" % port)

        for f in command["args"]["files"]:
            if not stderrs.exists(f):
                raise Exception("CHECK ERROR: %s not found" % f)

        return cd, envs
