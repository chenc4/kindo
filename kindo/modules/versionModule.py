#!/usr/bin/env python
#-*- coding: utf-8 -*-

from kindo.core.kindoCore import KindoCore


class VersionModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        self.logger.info("Version: %s" % self.kindo_version)
        self.logger.info("API Version: %s" % self.kindo_api_version)
