#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import shutil
from modules.kindoModule import KindoModule


class CleanModule(KindoModule):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoModule.__init__(self, command, startfolder, configs, options, logger)

    def start(self):
        shutil.rmtree(self.kindo_caches_path)
