#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import traceback
from kindo.kindo_core import KindoCore
from kindo.utils.config_parser import ConfigParser


class LogoutModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        ini_path = os.path.join(self.kindo_settings_path, "kindo.ini")
        if not os.path.isfile(ini_path):
            self.logger.info("logout successfully")
            return

        try:
            cf = ConfigParser(ini_path)
            cf.remove("default", "username")
            cf.remove("default", "password")
            cf.write()

            self.logger.info("logout successfully")
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e)
