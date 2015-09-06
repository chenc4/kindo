#!/usr/bin/env python
#-*- coding: utf-8 -*-

from prettytable import PrettyTable
from modules.kindoModule import KindoModule
from utils.configParser import ConfigParser


class ImagesModule(KindoModule):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoModule.__init__(self, command, startfolder, configs, options, logger)

    def start(self):
        images = self.get_images_list()

        table = PrettyTable(["Name", "Version", "Author", "Size", "BuildTime"])
        table.padding_width = 1

        for section, image in images.items():
            table.add_row([
                image.get("name", ""),
                image.get("version", "1.0"),
                image.get("author", "anonymous"),
                image.get("size", 0),
                image.get("buildtime", "")
                ]
            )

        self.logger.response(table)

    def get_images_list(self):
        ini_path = os.path.join(self.kindo_settings_path, "images.ini")
        if not os.path.isfile(ini_path):
            return {}

        cf = ConfigParser()
        cf.read(ini_path)

        images = {}
        for section in cf.sections():
            images[section] = {}

            items = cf.items(section)

            for k, v in items:
                k = k.strip()
                v = v.strip()
                images[section][k] = v
        return images