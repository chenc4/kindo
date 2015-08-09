#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from commands.command import Command


class Workdir(Command):
    def __init__(self):
        Command.__init__(self)

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
            return False

        if command["action"] != "WORKDIR":
            return False

        self.position = command["args"]["dir"]
        return True
