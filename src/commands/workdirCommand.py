#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
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

    def run(self, command, deps_folder, position):
        if "action" not in command:
            return -1, position, ""

        if command["action"] != "WORKDIR":
            return -1, position, ""

        return 1, command["args"]["dir"], ""
