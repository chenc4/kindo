#!/usr/bin/env python
#-*- coding: utf-8 -*-
from kindo.commands.command import Command


class WorkdirCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value, kic_path=None):
        if not value[8:]:
            return {}

        return {
            "action": "WORKDIR",
            "args": {"dir": value[8:]},
            "variables": []
        }

    def run(self, ssh_client, command, filesdir, imagesdir, cd, envs, ki_path=None):
        return command["args"]["dir"], envs
