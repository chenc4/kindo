#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
from kindo.kindo_core import KindoCore
from kindo.utils.prettytable import PrettyTable
from kindo.utils.config_parser import ConfigParser


class ImagesModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        images = self.get_images_list()

        table = PrettyTable(["Name", "Version", "Pusher", "Size", "BuildTime"])
        table.padding_width = 1

        for section in images:
            image = images[section]

            table.add_row([
                image.get("name", ""),
                image.get("version", "1.0"),
                image.get("author", "anonymous"),
                image.get("size", 0),
                image.get("buildtime", "")
            ])

        self.logger.info(table)

    def get_images_list(self):
        ini_path = os.path.join(self.kindo_settings_path, "images.ini")
        if not os.path.isfile(ini_path):
            return {}

        cf = ConfigParser(ini_path)

        return cf.get()
