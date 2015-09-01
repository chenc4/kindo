#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import traceback
import requests
import simplejson
import hashlib
from prettytable import PrettyTable
from fabric.operations import prompt
from core.kindoCore import KindoCore


class Search(KindoCore):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoCore.__init__(self, command, startfolder, configs, options, logger)

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

                table = PrettyTable(["number", "name", "version", "size"])
                index = 0
                for ki in response:
                    index += 1
                    table.add_row([index, ki["name"], ki["version"], ki["size"]])

                if len(response) == 0:
                    self.logger.warn("PACKAGE NOT FOUND: %s" % option)
                    continue

                self.logger.response(table)

                if len(response) == 1:
                    self.download_package(response[0]["url"], response[0]["name"])
                else:
                    number = self.get_input_number(response)
                    if number > -1:
                        self.download_package(response[number]["url"], response[number]["name"])
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

    def download_package(self, url, name):
        self.logger.info("downloading %s" % name)

        r = requests.get(url)
        if r.status_code == 200:
            name = name if name[-3:] == ".ki" else "%s.ki" % name

            if not os.path.isdir(self.kindo_packages_path):
                os.makedirs(self.kindo_packages_path)

            target = os.path.join(self.kindo_packages_path, name)
            with open(target, "wb") as fs:
                fs.write(r.content)










