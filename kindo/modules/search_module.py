#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import traceback

from kindo.kindo_core import KindoCore
from kindo.utils.config_parser import ConfigParser
from kindo.utils.prettytable import PrettyTable
from kindo.utils.functions import download_with_progressbar, prompt


class SearchModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        try:
            for option in self.options[2:]:
                self.logger.debug("searching %s" % option)

                isok, res = self.api.search(option)
                if not isok:
                    continue

                self.logger.debug("searched %s results" % len(res))

                table = PrettyTable(["number", "name", "version", "pusher", "size"])
                index = 0
                for ki in res:
                    index += 1
                    table.add_row([index, ki["name"], ki["version"], ki["pusher"], ki["size"]])

                if len(res) == 0:
                    continue

                self.logger.info(table)

                number = self.get_input_number(res)
                if number is not None and number > -1:
                    self.pull_image(res[number]["name"])
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e)

    def get_input_number(self, kis, max_times=3, now_time=0):
        if now_time < max_times:
            number = prompt("please input the number what you want to install:", default="")
            if not number:
                return
            try:
                number = int(number) - 1

                if number < 0 or number >= len(kis):
                    self.logger.error("number invalid")
                    return self.get_input_number(kis, max_times, now_time + 1)

                return number
            except:
                return self.get_input_number(kis, max_times, now_time + 1)

        return -1

    def pull_image(self, uniqueName):
        name, version = uniqueName.split(":") if ":"in uniqueName else (uniqueName, "")
        author, name = name.split("/") if "/" in name else ("", name)

        try:
            isok, res = self.api.pull(author, name, version)
            if not isok:
                self.logger.error(res)
                return

            if not self.add_image_info(res, self.download_package(res)):
                raise Exception("pull failed")

        except:
            self.logger.debug(traceback.format_exc())

    def download_package(self, image_info):
        url = image_info["url"]
        name = image_info["name"]

        if url is None or not url:
            return

        self.logger.debug("downloading %s" % name)

        kiname = name.replace("/", "-").replace(":", "-")
        kiname = kiname if name[-3:] == ".ki" else "%s.ki" % kiname
        target = os.path.join(self.kindo_images_path, kiname)

        if os.path.isfile(target):
            return target

        self.logger.debug(url)

        if not os.path.isdir(self.kindo_images_path):
            os.makedirs(self.kindo_images_path)

        download_with_progressbar(url, target)
        return target

    def add_image_info(self, image_info, path):
        if path is None or not path:
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
