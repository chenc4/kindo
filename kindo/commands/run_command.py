#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
import simplejson
from fabric.api import cd
from fabric.api import env
from fabric.context_managers import shell_env
from kindo.commands.command import Command


class RunCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value, kic_path=None):
        command_str = value[4:].strip()
        if not command_str:
            return {}

        try:
            if command_str[0] == "[" and command_str[-1] == "]":
                command_list = simplejson.loads(command_str)
                command_str = " ".join(command_list)
        except:
            pass

        return {
            "action": "RUN",
            "args": {"command": command_str},
            "files": [],
            "images": []
        }

    def run(self, command, filesdir, imagesdir, position, envs, ki_path=None):
        with cd(position):
            with shell_env(**envs):
                self.execute(command["args"]["command"])
        return position, envs
