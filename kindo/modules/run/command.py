#!/usr/bin/env python
#-*- coding: utf-8 -*-

from kindo.kindo_core import KindoCore


class Command(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

        self._system_info = None
