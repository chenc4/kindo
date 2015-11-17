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
        strs = self._get_content_info(value[4:])

        if len(strs) >= 2:
            f_file = strs[0]
            t_file = strs[1]

            if not f_file or not t_file:
                return {}

            filedir, filename = os.path.split(re.sub("[\?|\+|\*|\<|\>|:]", "", os.path.split(f_file)[1]))

            return {
                "action": "ADD",
                "args": {"from": filename, "to": t_file},
                "images": [],
                "files": [{"name": filename, "url": f_file}]
            }
        return {}

    def run(self, command, filesdir, imagesdir, position, envs):
        src = os.path.join(filesdir, command["args"]["from"])
        if not os.path.isfile(src):
            raise Exception("{0} not found".format(src))

        with cd(position):
            with shell_env(**envs):
                if not self.upload(src, command["args"]["to"]):
                    raise Exception("{0} upload failed".format(src))
                return position, envs
        return position, envs

    def _get_content_info(self, content):
        parts = [part.strip() for part in content.split("\"") if part != ""]
        if len(parts) == 1:
            if content[0] == "\"" and content[-1] == "\"":
                return parts[0], ""

            first_part_info = parts[0].split(" ")
            if len(first_part_info) > 1:
                return " ".join(first_part_info[:-1]), first_part_info[-1]
            return first_part_info[0], ""
        return parts[0], parts[1]
