#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import traceback
from utils.configParser import ConfigParser
from modules.kindoModule import KindoModule


class LogoutModule(KindoModule):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoModule.__init__(self, command, startfolder, configs, options, logger)

    def start(self):
        ini_path = os.path.join(self.kindo_settings_path, "kindo.ini")
        if not os.path.isfile(ini_path):
            self.logger.info("logout successfully")
            return

        try:
            cf = ConfigParser()
            cf.read(ini_path)


            if "default" in cf.sections():
                cf.remove_option("default", "username")
                cf.remove_option("default", "password")

            cf.write(open(ini_path, "w"))
            self.logger.info("logout successfully")
        except:
            self.logger.debug(traceback.format_exc())
            self.logger.error("logout failed")
