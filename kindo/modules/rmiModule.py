#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import traceback
from core.kindoCore import KindoCore
from utils.configParser import ConfigParser


class RmiModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        if len(self.options) < 3:
            self.logger.response("no images", False)
            return

        self.logger.debug(self.options)

        try:
            if self.delete_image(self.options[2]):
                self.logger.response("delete ok")
            else:
                self.logger.response("delete failed", False)
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.response(e, False)

    def delete_image(self, image_name):
        ini_path = os.path.join(self.kindo_settings_path, "images.ini")
        if not os.path.isfile(ini_path):
            return False

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
        return True
