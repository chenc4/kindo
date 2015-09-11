#!/usr/bin/env python
#-*- coding: utf-8 -*-

from core.kindoCore import KindoCore


class InfoModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        infos = """Version:        %s
API Version:    %s
Tmps Path:      %s
Caches Path:    %s
KICS Path:      %s
IMAGES Path:    %s
SETTINGS Path:  %s
""" % (self.kindo_version, self.kindo_api_version, self.kindo_tmps_path, self.kindo_caches_path, self.kindo_kics_path, self.kindo_images_path, self.kindo_settings_path)
        self.logger.info(infos)

        configs = self.get_kindo_setting()
        for k, v in configs.items():
            self.logger.info("%s: %s" % (k, v))
