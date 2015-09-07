#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import traceback
from utils.configParser import ConfigParser
from modules.kindoModule import KindoModule

class RmiModule(KindoModule):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoModule.__init__(self, command, startfolder, configs, options, logger)

    def start(self):
        if len(self.options) < 3:
            self.logger.warn("NO IMAGES")
            return

        self.logger.debug(self.options)

        try:
            self.delete_image(self.options[2])
        except:
            self.logger.debug(traceback.format_exc())
            self.logger.error("delete failed")

    def delete_image(self, image_name):
        ini_path = os.path.join(self.kindo_settings_path, "images.ini")
        if not os.path.isfile(ini_path):
            return {}

        cf = ConfigParser()
        cf.read(ini_path)

        sections = cf.sections()
        if image_name in sections:
            items = cf.items(image_name)

            self.logger.debug(items)

            kiname = ""
            for k, v in items:
                if k == "name":
                    kiname = v.replace("/", "-").replace(":", "-")

                    if kiname[-3:] != ".ki":
                        kiname = "%s.ki" % kiname
                    break

            target = os.path.join(self.kindo_images_path, kiname)
            if os.path.isfile(target):
                os.remove(target)

            cf.remove_section(image_name)
            cf.write(open(ini_path, "w"))
