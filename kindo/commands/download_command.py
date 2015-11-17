#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.api import cd
from fabric.context_managers import shell_env
from kindo.commands.command import Command


class DownloadCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value):
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

    def run(self, command, filesdir, imagesdir, position, envs):
        with cd(position):
            with shell_env(**envs):
                target = os.path.realpath(command["args"]["to"])
                if os.path.isfile(target):
                    os.remove(target)

                if command["args"]["from"][:7].lower() != "http://" and command["args"]["from"][:8].lower() != "https://":
                    if not self.download(command["args"]["from"], target):
                        raise Exception("{0} download failed".format(command["args"]["from"]))
                else:
                    if not self.download_by_url(command["args"]["from"], target):
                        raise Exception("{0} download failed".format(command["args"]["from"]))
                return position, envs
        return position, envs
