#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import requests
import hashlib
import traceback
from fabric.operations import prompt
from core.errors import ERRORS
from utils.configParser import ConfigParser
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

            if not self.add_image_info(response, self.download_package(response)):
                self.logger.error("pull failed")

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

    def download_package(self, image_info):
        url = image_info["url"]
        name = image_info["name"]

        self.logger.info("downloading %s from %s" % (name, url))

        kiname = name.replace("/", "-").replace(":", "-")
        kiname = kiname if name[-3:] == ".ki" else "%s.ki" % kiname
        target = os.path.join(self.kindo_images_path, kiname)

        if os.path.isfile(target):
            self.logger.debug("%s existed, removing" % target)
            os.remove(target)

        r = requests.get(url)
        if r.status_code == 200:
            if not os.path.isdir(self.kindo_images_path):
                os.makedirs(self.kindo_images_path)

            with open(target, "wb") as fs:
                fs.write(r.content)
            return target
        else:
            self.logger.error("download failed")
            self.logger.debug(r.content)
        return ""

    def add_image_info(self, image_info, path):
        if not path:
            self.logger.debug("path is empty")
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


