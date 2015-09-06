#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import requests
import hashlib
import traceback
from fabric.operations import prompt
from core.errors import ERRORS
from modules.kindoModule import KindoModule


class PullModule(KindoModule):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoModule.__init__(self, command, startfolder, configs, options, logger)

    def start(self):
        pull_engine_url = self.get_pull_engine_url()
        try:
            if len(self.options) < 3:
                self.logger.warn("NO IMAGE NAME")
                return

            response = self.pull_image_info(pull_engine_url)
            if response is None:
                return

            if "code" in response:
                if response["code"] == "040014000":
                    code = prompt("please input the extraction code: ")
                    response = self.pull_image_info(pull_engine_url, {"code": code})

                if "code" in response:
                    self.logger.error(response["msg"])
                    return
            self.download_package(response)
            self.add_image_info(response)
        except:
            self.logger.debug(traceback.format_exc())
            self.logger.error("\"%s\" can't connect" % pull_engine_url)



    def get_pull_engine_url(self):
        pull_engine_url = "%s/v1/pull" % self.configs.get("index", "kindo.cycore.cn")

        if pull_engine_url[:7].lower() != "http://" and pull_engine_url[:8].lower() != "https://":
            pull_engine_url = "http://%s" % pull_engine_url

        return pull_engine_url

    def pull_image_info(self, pull_engine_url, params=None):
        name, version = self.options[2].split(":") if ":"in self.options[2] else (self.options[2], "")
        author, name = name.split("/") if "/" in name else ("", name)

        params = dict({"name": name}, **params) if params is not None else {"name": name}
        if not author:
            params["author"] = author

        if not version:
            params["version"] = version

        if "username" in self.configs:
            params["username"] = self.configs["username"]

        if "password" in self.configs:
            params["token"] = hashlib.new("md5", self.configs["password"]).hexdigest()

        r = requests.get(pull_engine_url, params=params)
        if r.status_code != 200:
            self.logger.error("\"%s\" can't connect" % pull_engine_url)
            return

        return r.json()

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


