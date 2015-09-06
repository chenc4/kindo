#!/usr/bin/env python
#-*- coding: utf-8 -*-

from modules.kindoModule import KindoModule


class VersionModule(KindoModule):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoModule.__init__(self, command, startfolder, configs, options, logger)

    def start(self):
        self.logger.response("Version: %s" % self.kindo_version)
        self.logger.response("API Version: %s" % self.kindo_api_version)
