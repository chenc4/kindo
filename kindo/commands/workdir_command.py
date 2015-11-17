#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.context_managers import shell_env
from kindo.commands.command import Command


class WorkdirCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value):
        if not value[8:]:
            return {}

        return {
            "action": "WORKDIR",
            "args": {"dir": value[8:]},
            "variables": []
        }

    def run(self, command, filesdir, imagesdir, position, envs):
        return command["args"]["dir"], envs
