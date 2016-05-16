#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import traceback
from kindo.kindo_core import KindoCore
from kindo.utils.config_parser import ConfigParser


class RmiModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        if len(self.options) < 3:
            self.logger.error("no images")
            return

        self.logger.debug(self.options)

        try:
            for option in self.options[2:]:
                if self.delete_image(option):
                    self.logger.info("delete ok")
                else:
                    self.logger.error("delete failed")
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e, False)

    def delete_image(self, image_name):
        ini_path = os.path.join(self.kindo_settings_path, "images.ini")
        if not os.path.isfile(ini_path):
            return False

        cf = ConfigParser(ini_path)
        infos = cf.get()

        if image_name not in infos:
            return True

        if "path" in infos[image_name]:
            target = infos[image_name]["path"]
            if os.path.isfile(target):
                os.remove(target)

        cf.remove(image_name)
        cf.write()
        return True
