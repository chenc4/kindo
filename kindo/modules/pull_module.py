#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import traceback
from kindo.kindo_core import KindoCore
from kindo.utils.config_parser import ConfigParser
from kindo.utils.functions import download_with_progressbar


class PullModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        try:
            if len(self.options) < 3:
                self.logger.error("image no found")
                return

            name, version = self.options[2].split(":") if ":"in self.options[2] else (self.options[2], "")
            author, name = name.split("/") if "/" in name else ("", name)

            isok, res = self.api.pull(self.get_kindo_setting("username") if not author else author, name, version)
            if not isok:
                self.logger.error(res)
                return

            if not self.add_image_info(res, self.download_package(res)):
                raise Exception("pull failed")

        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e)

    def download_package(self, image_info):
        url = image_info["url"]
        name = image_info["name"]

        self.logger.debug("downloading %s from %s" % (name, url))

        kiname = name.replace("/", "-").replace(":", "-")
        kiname = kiname if name[-3:] == ".ki" else "%s.ki" % kiname
        target = os.path.join(self.kindo_images_path, kiname)

        if os.path.isfile(target):
            self.logger.debug("%s existed, removing" % target)
            os.remove(target)

        if not os.path.isdir(self.kindo_images_path):
            os.makedirs(self.kindo_images_path)

        try:
            download_with_progressbar(url, target)
        except:
            raise Exception("\"%s\" can't be downloaded" % url)
        return target

    def add_image_info(self, image_info, path):
        if not path:
            self.logger.debug("path is empty")
            return False

        ini_path = os.path.join(self.kindo_settings_path, "images.ini")
        if not os.path.isdir(self.kindo_settings_path):
            os.makedirs(self.kindo_settings_path)

        cf = ConfigParser(ini_path)
        cf.set(image_info["name"], "name", image_info["name"])
        cf.set(image_info["name"], "version", image_info["version"])
        cf.set(image_info["name"], "buildtime", image_info["buildtime"])
        cf.set(image_info["name"], "pusher", image_info["pusher"])
        cf.set(image_info["name"], "size", image_info["size"])
        cf.set(image_info["name"], "url", image_info["url"])
        cf.set(image_info["name"], "path", path)
        cf.write()

        return True
