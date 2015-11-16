#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.api import cd
from fabric.context_managers import shell_env
from kindo.commands.command import Command


class AddCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

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
                    "images": [],
                    "files": [f_file]
                }
        return {}

    def run(self, command, filesdir, imagesdir, position, envs):
        src = os.path.join(filesdir, command["args"]["from"])
        if not os.path.isfile(src):
            raise Exception("{0} not found".format(src))

        with cd(position):
            with shell_env(**envs):
                if not self.upload(src, command["args"]["to"]):
                    raise Exception("{0} upload failed"format(src))
                return position, envs
        return position, envs
