#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
from modules.kindoModule import KindoModule

class RmiModule(KindoModule):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoModule.__init__(self, command, startfolder, configs, options, logger)

    def start(self):
        if len(self.options) < 3:
            self.logger.warn("NO IMAGES")
            return

        self.delete_image(self.options[2])

    def delete_image(self, image_name):
        image_name = image_name.replace("/", "-").replace(":", "-")

        ini_path = os.path.join(self.kindo_settings_path, "images.ini")
        if not os.path.isfile(ini_path):
            return {}

        cf = ConfigParser()
        cf.read(ini_path)

        sections = cf.sections()
        for section in sections:
            options = cf.options(section)

            author = options.get("author", "anonymous")
            version = options.get("version", "1.0")
            name = options.get("name", "")

            if name != image_name and section != image_name:
                continue

            kiname = "%s-%s-%s.ki" % (name[:-3], version) if name[-3:] == ".ki" else "%s-%s-%s.ki" % (author, name, version)
            target = os.path.join(self.kindo_images_path, kiname)
            if os.path.isfile(target):
                os.remove(target)

            cf.remove_section(section)
