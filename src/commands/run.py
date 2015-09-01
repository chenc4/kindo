#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.api import cd
from fabric.api import env
from commands.command import Command


class Run(Command):
    def __init__(self):
        Command.__init__(self)

    def parse(self, value):
        value = value.strip()
        if len(value) > 4 and value[:4].lower() == "run ":
            return {
                "action": "RUN",
                "args": {"command": value[4:]},
                "variables": []
            }
        return {}

    def run(self, command, deps_folder, position):
        if "action" not in command:
            return -1, position, ""

        if command["action"] != "RUN":
            return -1, position, ""

        with cd(position):
            self.execute(command["args"]["command"])
        return 1, position, ""
