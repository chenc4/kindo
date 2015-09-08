#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.api import cd
from commands.command import Command
from utils.configParser import ConfigParser


class AddOnRunCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value):
        value = value.strip()
        if len(value) > 9 and value[:9].lower() == "addonrun ":
            strs = re.split("\s+", value[9:])

            if len(strs) >= 2:
                f_file = strs[0]
                t_file = strs[1]

                return {
                    "action": "ADDONRUN",
                    "args": {"from": f_file, "to": t_file},
                    "variables": [],
                    "files": []
                }
        return {}

    def run(self, command, deps_folder, position=None):
        if "action" not in command:
            return -1, position, ""

        if command["action"] != "ADDONRUN":
            return -1, position, ""

        src = command["args"]["from"]
        if not os.path.isfile(src) and not os.path.isdir(src):
            src = os.path.realpath(command["args"]["from"])
            if not os.path.isfile(src) and not os.path.isdir(src):
                src = os.path.join(self.startfolder, command["args"]["from"])
                if not os.path.isfile(src) and not os.path.isdir(src):
                    src = os.path.join(os.path.dirname(self.get_ki_path()), command["args"]["from"])

        ignore = True if self.configs.get("ignore", 1) == 1 else False
        if not os.path.isfile(src) and not os.path.isdir(src):
            if ignore:
                return 1, position, ""
            return 0, position, "ADDONRUN ERROR: %s not found" % src

        with cd(position):
            if not self.upload(src, command["args"]["to"]):
                return 0, position, "ADDONRUN ERROR: %s upload failed" % src
            return 1, position, ""
        return -1, position, ""


    def get_ki_path(self):
        self.logger.debug(self.options)

        ki_path = ""
        for option in self.options:
            ki_path = option
            if ki_path[-3:] != ".ki":
                ki_path = "%s.ki" % ki_path


            if not os.path.isfile(ki_path):
               path = os.path.realpath(ki_path)
               if not os.path.isfile(path):
                    path = os.path.join(self.startfolder, "images", ki_path)
                    if not os.path.isfile(path):
                        path = os.path.join(self.startfolder, ki_path)
                        if not os.path.isfile(path):
                            path = self.get_image_path(option)

                    if os.path.isfile(path):
                        ki_path = path

            if os.path.isfile(ki_path):
                break

        self.logger.debug(ki_path)
        return ki_path

    def get_image_path(self, section):
        ini_path = os.path.join(self.kindo_settings_path, "images.ini")
        if not os.path.isfile(ini_path):
            return {}

        cf = ConfigParser()
        cf.read(ini_path)

        sections = cf.sections()

        if section in sections:
            items = cf.items(section)

            for k, v in items:
                if k == "path":
                    return v
        return ""
