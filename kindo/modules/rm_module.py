#!/usr/bin/env python
#-*- coding: utf-8 -*-

import traceback
from kindo.kindo_core import KindoCore


class RmModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        if len(self.options) < 3:
            self.logger.error("no images", False)
            return

        try:
            for option in self.options[2:]:
                self.delete_image(option)
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e, False)

    def delete_image(self, image_name):
        name, version = image_name.split(":") if ":"in image_name else (image_name, "")
        author, name = name.split("/") if "/" in name else (self.configs.get("default", {}).get("username", ""), name)

        if not author or not name or not version:
            self.logger.error("invalid image name")
            return

        isok, res = self.api.rm(
            author,
            name,
            version,
            self.configs.get("default", {}).get("username", ""),
            self.configs.get("default", {}).get("password", "")
        )
        if not isok:
            self.logger.error(res)
            return

        self.logger.info("delete %s successfully" % image_name)
