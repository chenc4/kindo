#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import traceback
import requests
import simplejson
import zipfile
import hashlib
from prettytable import PrettyTable
from fabric.operations import prompt
from utils.configParser import ConfigParser
from modules.kindoModule import KindoModule


class SearchModule(KindoModule):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoModule.__init__(self, command, startfolder, configs, options, logger)

    def start(self):
        search_engine_url = "%s/v1/search" % self.configs.get("index", "kindo.cycore.cn")

        if search_engine_url[:7].lower() != "http://" and search_engine_url[:8].lower() != "https://":
            search_engine_url = "http://%s" % search_engine_url

        for option in self.options[2:]:
            try:
                self.logger.info("searching %s" % option)

                params = {"q": option}

                self.logger.info("connecting %s" % search_engine_url)
                r = requests.get(search_engine_url, params=params)
                if r.status_code != 200:
                    self.logger.error("\"%s\" can't connect" % search_engine_url)
                    return

                response = r.json()

                if "code" in response:
                    self.logger.error(response["msg"])
                    return

                self.logger.info("searched %s results" % len(response))

                table = PrettyTable(["number", "name", "version", "pusher", "size"])
                index = 0
                for ki in response:
                    index += 1
                    table.add_row([index, ki["name"], ki["version"], ki["pusher"], ki["size"]])

                if len(response) == 0:
                    self.logger.warn("IMAGE NOT FOUND: %s" % option)
                    continue

                self.logger.response(table)

                if len(response) == 1:
                    self.pull_image(response[0]["name"])
                else:
                    number = self.get_input_number(response)
                    if number > -1:
                        self.pull_image(response[number]["name"])
            except:
                self.logger.debug(traceback.format_exc())
                self.logger.error("\"%s\" can't connect" % search_engine_url)

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

        self.logger.info("downloading %s" % name)

        kiname = name.replace("/", "-").replace(":", "-")
        kiname = kiname if name[-3:] == ".ki" else "%s.ki" % kiname
        target = os.path.join(self.kindo_images_path, kiname)

        if os.path.isfile(target):
            return target

        self.logger.debug(url)

        r = requests.get(url)
        if r.status_code == 200:
            if not os.path.isdir(self.kindo_images_path):
                os.makedirs(self.kindo_images_path)

            with open(target, "wb") as fs:
                fs.write(r.content)
            return target

        return ""

    def pull_image(self, name):
        pull_engine_url = self.get_pull_engine_url()
        try:
            self.logger.info("pulling image info: %s" % name)

            response = self.pull_image_info(pull_engine_url, name)
            if response is None:
                return

            if "code" in response:
                if response["code"] == "040014000":
                    code = prompt("please input the extraction code: ")

                    self.logger.info("pulling image info again: %s" % name)
                    response = self.pull_image_info(pull_engine_url, name, {"code": code})

                if "code" in response:
                    self.logger.error(response["msg"])
                    return

            if not self.add_image_info(response, self.download_package(response)):
                self.logger.error("pull failed")

        except:
            self.logger.debug(traceback.format_exc())
            self.logger.error("\"%s\" can't connect" % pull_engine_url)

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
            self.logger.error("\"%s\" can't connect" % pull_engine_url)
            return

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

        cf = ConfigParser()
        cf.read(ini_path)

        sections = cf.sections()

        if image_info["name"] not in sections:
            cf.add_section(image_info["name"])

        cf.set(image_info["name"], "name", image_info["name"])
        cf.set(image_info["name"], "version", image_info["version"])
        cf.set(image_info["name"], "buildtime", image_info["buildtime"])
        cf.set(image_info["name"], "pusher", image_info["pusher"])
        cf.set(image_info["name"], "size", image_info["size"])
        cf.set(image_info["name"], "url", image_info["url"])
        cf.set(image_info["name"], "path", path)

        cf.write(open(ini_path, "w"))

        return True








