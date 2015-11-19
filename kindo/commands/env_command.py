#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.api import cd
from kindo.commands.command import Command


class EnvCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value):
        strs = re.split("[\s|=]+", value[4:])

        if len(strs) >= 2:
            env_key = strs[0]
            env_value = strs[1]

            return {
                "action": "ENV",
                "args": {"key": env_key, "value": env_value},
                "variables": [],
                "files": []
            }
        return {}

    def run(self, command, filesdir, imagesdir, position, envs):
        envs[command["args"]["key"]] = command["args"]["value"]

        return position, envs
