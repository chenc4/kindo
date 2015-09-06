#!/usr/bin/env python
#-*- coding: utf-8 -*-

from modules.kindoModule import KindoModule


class InfoModule(KindoModule):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoModule.__init__(self, command, startfolder, configs, options, logger)

    def start(self):
        infos = """Version:        %s
API Version:    %s
Tmps Path:      %s
Caches Path:    %s
KICS Path:      %s
IMAGES Path:    %s
SETTINGS Path:  %s
""" % (self.kindo_version, self.kindo_api_version, self.kindo_tmps_path, self.kindo_caches_path, self.kindo_kics_path, self.kindo_images_path, self.kindo_settings_path)
        self.logger.response(infos)
        
        configs = self.get_kindo_setting()
        for k, v in configs.items():
            self.logger.response("%s: %s" % (k, v))
