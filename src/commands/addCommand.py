#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.api import cd
from commands.command import Command


class AddCommand(Command):
    def __init__(self):
        Command.__init__(self)

    def parse(self, value):
        value = value.strip()
        if len(value) > 4 and value[:4].lower() == "add ":
            strs = re.split("\s+", value[4:])

            if len(strs) >= 2:
                f_file = strs[0]
                t_file = strs[1]

                filename = re.sub("[\?|\+|\*|\<|\>|:]", "", os.path.split(f_file)[1])

                return {
                    "action": "ADD",
                    "args": {"from": filename, "to": t_file},
                    "variables": [],
                    "files": [f_file]
                }
        return {}

    def run(self, command, deps_folder, position=None):
        if "action" not in command:
            return -1, position, ""

        if command["action"] != "ADD":
            return -1, position, ""

        src = os.path.join(deps_folder, command["args"]["from"])
        if not os.path.isfile(src):
            return 0, position, "ADD ERROR: %s not found" % src

        with cd(position):
            if not self.upload(src, command["args"]["to"]):
                return 0, position, "ADD ERROR: %s upload failed" % src
            return 1, position, ""
        return -1, position, ""
