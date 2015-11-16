#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
import time
from fabric.api import cd
from fabric.api import env
from fabric.context_managers import shell_env
from kindo.commands.command import Command


class CentOSCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value):
        value = value.strip()

        if len(value) > 7 and value[:7].lower() == "centos ":
            return {
                "action": "CENTOS",
                "args": {"command": value[7:]},
                "variables": []
            }
        return {}

    def run(self, command, depsdir, position, envs):
        if "CentOS" in self.get_system_info()["system"]:
            with cd(position):
                with shell_env(**envs):
                    self.execute(command["args"]["command"])

            return 1, position, "", envs
        return -1, position, "", envs
