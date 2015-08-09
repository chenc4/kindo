#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.api import cd
from commands.command import Command


class Add(Command):
    def __init__(self):
        Command.__init__(self)

    def parse(self, value):
        value = value.strip()
        if len(value) > 4 and value[:4].lower() == "add ":
            strs = re.split("\s+", value[4:])

            if len(strs) >= 2:
                f_file = strs[0]
                t_file = strs[1]

                self.deps.append(f_file)

                filename = re.split("[\?|\+|\*|\<|\>|:]", os.path.split(f_file)[1])

                return {
                    "action": "ADD",
                    "args": {"from": filename[0], "to": t_file},
                    "variables": []
                }
        return {}

    def run(self, command, deps_folder, position=None):
        if "action" not in command:
            return False

        if command["action"] != "ADD":
            return False

        src = os.path.join(deps_folder, command["args"]["from"])
        if not os.path.isfile(src):
            raise Exception("%s not existed" % src)

        with cd(position):
            self.position = position
            if not self.upload(src, command["args"]["to"]):
                raise Exception("upload failed")
        return False
