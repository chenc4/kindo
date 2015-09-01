#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
import time
from fabric.api import cd
from fabric.api import env
from commands.command import Command


class CentOS(Command):
    def __init__(self):
        Command.__init__(self)

    def parse(self, value):
        value = value.strip()

        if len(value) > 7 and value[:7].lower() == "centos ":
            return {
                "action": "CENTOS",
                "args": {"command": value[7:]},
                "variables": []
            }
        return {}

    def run(self, command, deps_folder, position):
        if "action" not in command:
            return -1, position, ""

        if command["action"] != "CENTOS":
            return -1, position, ""

        if "CentOS" in self.get_system_info()["system"]:
            with cd(position):
                self.execute(command["args"]["command"])

            return 1, position, ""
        return -1, position, ""
