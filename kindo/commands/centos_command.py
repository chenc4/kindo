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
        if not value[7:]:
            return {}

        return {
            "action": "CENTOS",
            "args": {"command": value[7:]},
            "files": [],
            "images": []
        }

    def run(self, command, filesdir, imagesdir, position, envs):
        if "CentOS" in self.get_system_info()["system"]:
            with cd(position):
                with shell_env(**envs):
                    self.execute(command["args"]["command"])

            return position, envs
        return position, envs
