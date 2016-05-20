#!/usr/bin/env python
#-*- coding: utf-8 -*-
from kindo.modules.run.command import Command


class FromCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value, kic_path=None):
        value = value[5:]

        if not value:
            return {}

        image_info = {}
        image_name = "{0}.ki".format(image_info["name"].replace("/", "-").replace(":", "-"))

        return {
            "action": "FROM",
            "args": {"url": image_info["url"], "name": image_name},
            "files": [],
            "images": [{"url": image_info["url"], "name": image_name}]
        }

    def run(self, ssh_client, command, filesdir, imagesdir, cd, envs, ki_path=None):
        return cd, envs
