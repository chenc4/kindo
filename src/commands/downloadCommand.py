#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.api import cd
from fabric.context_managers import shell_env
from commands.command import Command


class DownloadCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value):
        value = value.strip()
        if len(value) > 9 and value[:9].lower() == "download ":
            strs = re.split("\s+", value[9:])

            if len(strs) > 1:
                f_file = strs[0]
                t_file = strs[1]

                return {
                    "action": "DOWNLOAD",
                    "args": {"from": f_file, "to": t_file},
                    "variables": []
                }
        return {}

    def run(self, command, depsdir, position, envs):
        with cd(position):
            with shell_env(**envs):
                target = os.path.realpath(command["args"]["to"])
                if os.path.isfile(target):
                    os.remove(target)

                if command["args"]["from"][:7].lower() != "http://" and command["args"]["from"][:8].lower() != "https://":
                    if not self.download(command["args"]["from"], target):
                        return 0, position, "DOWNLOAD ERROR: %s download failed" % command["args"]["from"], envs
                else:
                    if not self.download_by_url(command["args"]["from"], target):
                        return 0, position, "DOWNLOAD ERROR: %s download failed" % command["args"]["from"], envs
                return 1, position, "", envs
        return -1, position, "", envs
