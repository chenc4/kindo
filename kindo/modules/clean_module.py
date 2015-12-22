#!/usr/bin/env python
#-*- coding: utf-8 -*-

import shutil
from kindo.kindo_core import KindoCore


class CleanModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        shutil.rmtree(self.kindo_caches_path)
