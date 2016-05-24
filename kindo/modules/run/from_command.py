#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import uuid
from kindo.modules.run.command import Command
from kindo.utils.functions import download_with_progressbar


class FromCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value, kic_path=None):
        value = value[5:]

        if not value:
            return {}

        value = value.strip('"')
        target = os.path.join(self.kindo_tmps_path, "{}.ki".format(str(uuid.uuid4())))
        if value[:7] == "http://" or value[:8] == "https://" and value[-3:] == ".ki":
            _, image_name = os.path.split(value)
            download_with_progressbar(value, target)
        elif value[-3:] == ".ki":
            _, image_name = os.path.split(value)
            target = os.path.realpath(value)
            if not os.path.isfile(target):
                kic_folder = os.path.dirname(kic_path)
                target = os.path.join(kic_folder, value)
        elif ":" in value and "/" in value:
            name, version = value.split(":") if ":"in value else (value, "")
            author, name = name.split("/") if "/" in name else ("", name)

            isok, res = self.api.pull(self.get_kindo_setting("username") if not author else author, name, version)
            if isok:
                download_with_progressbar(value, target)
                image_name = "{0}.ki".format(res["name"].replace("/", "-").replace(":", "-"))

        if not os.path.isfile(target):
            return {}

        return {
            "action": "FROM",
            "args": {"url": target, "name": image_name},
            "files": [],
            "images": [{"url": target, "name": image_name}]
        }

    def run(self, ssh_client, command, filesdir, imagesdir, cd, envs, ki_path=None):
        return cd, envs
