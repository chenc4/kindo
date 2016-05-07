#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import traceback
import requests

from kindo.utils.fabric.operations import prompt
from kindo.kindo_core import KindoCore
from kindo.utils.config_parser import ConfigParser
from kindo.utils.prettytable import PrettyTable
from kindo.utils.functions import download_with_progressbar


class SearchModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        search_engine_url = "%s/v1/search" % self.configs.get("index", self.kindo_default_hub_host)

        if search_engine_url[:7].lower() != "http://" and search_engine_url[:8].lower() != "https://":
            search_engine_url = "http://%s" % search_engine_url

        try:
            for option in self.options[2:]:
                self.logger.debug("searching %s" % option)

                params = {"q": option}

                self.logger.debug("connecting %s" % search_engine_url)
                r = requests.get(search_engine_url, params=params)
                if r.status_code != 200:
                    self.logger.error("\"%s\" can't connect" % search_engine_url)
                    return

                response = r.json()

                if "code" in response:
                    raise Exception(response["msg"])

                self.logger.debug("searched %s results" % len(response))

                table = PrettyTable(["number", "name", "version", "pusher", "size"])
                index = 0
                for ki in response:
                    index += 1
                    table.add_row([index, ki["name"], ki["version"], ki["pusher"], ki["size"]])

                if len(response) == 0:
                    self.logger.error("image not found: %s" % option)
                    continue

                self.logger.info(table)

                number = self.get_input_number(response)
                if number > -1:
                    self.pull_image(response[number]["name"])
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e)

    def get_input_number(self, kis, max_times=3, now_time=0):
        if now_time < max_times:
            number = prompt("please input the number what you want to install", default="1")
            try:
                number = int(number) - 1

                if number < 0 or number >= len(kis):
                    self.logger.error("number invalid")
                    return self.get_input_number(kis, max_times, now_time + 1)

                return number
            except:
                return self.get_input_number(kis, max_times, now_time + 1)

        return -1

    def download_package(self, image_info):
        url = image_info["url"]
        name = image_info["name"]

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

    def pull_image(self, name):
        pull_engine_url = self.get_pull_engine_url()
        try:
            self.logger.debug("pulling image info: %s" % name)

            response = self.pull_image_info(pull_engine_url, name)
            if response is None:
                return

            if "code" in response:
                if response["code"] == "040014000":
                    code = prompt("please input the extraction code: ")

                    self.logger.debug("pulling image info again: %s" % name)
                    response = self.pull_image_info(pull_engine_url, name, {"code": code})

                if "code" in response:
                    raise Exception(response["msg"])

            if not self.add_image_info(response, self.download_package(response)):
                raise Exception("pull failed")

        except:
            self.logger.debug(traceback.format_exc())

    def pull_image_info(self, pull_engine_url, name, params=None):
        name, version = name.split(":") if ":"in name else (name, "")
        author, name = name.split("/") if "/" in name else ("", name)

        params = dict({"uniqueName": name}, **params) if params is not None else {"uniqueName": name}
        if author:
            params["uniqueName"] = "%s/%s" % (author, params["uniqueName"])
        else:
            params["uniqueName"] = "anonymous/%s" % params["uniqueName"]

        if version:
            params["uniqueName"] = "%s:%s" % (params["uniqueName"], version)
        else:
            params["uniqueName"] = "%s:1.0" % params["uniqueName"]

        r = requests.get(pull_engine_url, params=params)
        if r.status_code != 200:
            raise Exception("\"%s\" can't connect" % pull_engine_url, False)

        return r.json()

    def get_pull_engine_url(self):
        pull_engine_url = "%s/v1/pull" % self.configs.get("index", "kindo.cycore.cn")

        if pull_engine_url[:7].lower() != "http://" and pull_engine_url[:8].lower() != "https://":
            pull_engine_url = "http://%s" % pull_engine_url

        return pull_engine_url

    def add_image_info(self, image_info, path):
        if not path:
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
