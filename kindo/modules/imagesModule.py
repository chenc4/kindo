#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
from core.kindoCore import KindoCore
from utils.prettytable import PrettyTable
from utils.configParser import ConfigParser


class ImagesModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        images = self.get_images_list()

        table = PrettyTable(["Name", "Version", "Pusher", "Size", "BuildTime"])
        table.padding_width = 1

        for section, image in images.items():
            table.add_row([
                image.get("name", ""),
                image.get("version", "1.0"),
                image.get("pusher", "anonymous"),
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
