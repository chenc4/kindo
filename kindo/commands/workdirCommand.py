#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.context_managers import shell_env
from commands.command import Command



class WorkdirCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value):
        value = value.strip()
        if len(value) > 8 and value[:8].lower() == "workdir ":
            return {
                "action": "WORKDIR",
                "args": {"dir": value[8:]},
                "variables": []
            }
        return {}

    def run(self, command, depsdir, position, envs):
        return 1, command["args"]["dir"], "", envs
