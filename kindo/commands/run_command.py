#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.api import cd
from fabric.api import env
from fabric.context_managers import shell_env
from kindo.commands.command import Command


class RunCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value):
        value = value.strip()
        if len(value) > 4 and value[:4].lower() == "run ":
            return {
                "action": "RUN",
                "args": {"command": value[4:]},
                "variables": []
            }
        return {}

    def run(self, command, depsdir, position, envs):
        with cd(position):
            with shell_env(**envs):
                self.execute(command["args"]["command"])
        return 1, position, "", envs
