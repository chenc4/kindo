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
        if not value[4:]:
            return {}

        return {
            "action": "RUN",
            "args": {"command": value[4:]},
            "files": [],
            "images": []
        }

    def run(self, command, filesdir, imagesdir, position, envs):
        with cd(position):
            with shell_env(**envs):
                self.execute(command["args"]["command"])
        return position, envs
