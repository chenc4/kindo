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
                if "username" in self.configs:
                    params["username"] = self.configs["username"]

                if "password" in self.configs:
                    params["token"] = hashlib.new("md5", self.configs["password"]).hexdigest()

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

                table = PrettyTable(["number", "name", "version", "author", "size"])
                index = 0
                for ki in response:
                    index += 1
                    table.add_row([index, ki["name"], ki["version"], ki["author"], ki["size"]])

                if len(response) == 0:
                    self.logger.warn("PACKAGE NOT FOUND: %s" % option)
                    continue

                self.logger.response(table)

                if len(response) == 1:
                    self.download_package(response[0])
                    self.add_image_info(response[0])
                else:
                    number = self.get_input_number(response)
                    if number > -1:
                        self.download_package(response[number])
                        self.add_image_info(response[number])
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
        author = image_info["author"]
        version = image_info["version"]

        self.logger.info("downloading %s" % name)

        kiname = "%s-%s-%s.ki" % (name[:-3], version) if name[-3:] == ".ki" else "%s-%s-%s.ki" % (author, name, version)
        target = os.path.join(self.kindo_images_path, kiname)

        if os.path.isfile(target):
            return True

        r = requests.get(url)
        if r.status_code == 200:
            if not os.path.isdir(self.kindo_images_path):
                os.makedirs(self.kindo_images_path)


            with open(target, "wb") as fs:
                fs.write(r.content)
            return True

        return False

    def add_image_info(self, image_info):
        ini_path = os.path.join(self.kindo_settings_path, "images.ini")
        if not os.path.isfile(ini_path):
            return {}

        cf = ConfigParser()
        cf.read(ini_path)

        sections = cf.sections()

        section = "%s-%s-%s" % (image_info["author"], image_info["name"], image_info["version"])
        if section not in sections:
            cf.add_section(section)
            cf.set(image_info["name"], "name", image_info["name"])
            cf.set(image_info["name"], "version", image_info["version"])
            cf.set(image_info["name"], "buildtime", image_info["buildtime"])
            cf.set(image_info["name"], "author", image_info["author"])
            cf.set(image_info["name"], "size", image_info["size"])










