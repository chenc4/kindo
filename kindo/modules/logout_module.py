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
            self.logger.response("logout successfully")
            return

        try:
            cf = ConfigParser()
            cf.read(ini_path)

            if "default" in cf.sections():
                cf.remove_option("default", "username")
                cf.remove_option("default", "password")

            cf.write(open(ini_path, "w"))
            self.logger.response("logout successfully")
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.response(e, False)
