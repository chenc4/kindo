#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from kindo.commands.command import Command
from kindo.utils.functions import download_with_progressbar


class DownloadCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value, kic_path=None):
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

    def run(self, ssh_client, command, filesdir, imagesdir, cd, envs, ki_path=None):
        target = os.path.realpath(command["args"]["to"])

        if command["args"]["from"][:7].lower() != "http://" and command["args"]["from"][:8].lower() != "https://":
            if not ssh_client.get(command["args"]["from"], target):
                raise Exception("{0} download failed".format(command["args"]["from"]))
        else:
            download_with_progressbar(command["args"]["from"], target)
            if not os.path.isfile(target):
                raise Exception("{0} download failed".format(command["args"]["from"]))
        return cd, envs
