#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import hashlib
import traceback
import requests
from utils.configParser import ConfigParser
from modules.kindoModule import KindoModule


class RmModule(KindoModule):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoModule.__init__(self, command, startfolder, configs, options, logger)

    def start(self):
        if len(self.options) < 3:
            self.logger.warn("NO IMAGES")
            return

        self.logger.debug(self.options)

        try:
            self.delete_image(self.options[2])
        except:
            self.logger.debug(traceback.format_exc())
            self.logger.error("delete failed")

    def delete_image(self, image_name):
        name, version = image_name.split(":") if ":"in image_name else (image_name, "")
        author, name = name.split("/") if "/" in name else (self.configs.get("username", "anonymous"), name)


        image_name = "%s/%s:%s" % (author, name, version)

        data = {"uniqueName": image_name}
        if "username" in self.configs:
            data["username"] = self.configs["username"]

        if "password" in self.configs:
            data["token"] = hashlib.new("md5", self.configs["password"]).hexdigest()

        delete_engine_url = self.get_delete_engine_url()

        self.logger.info("connecting %s" % delete_engine_url)

        r = requests.post(delete_engine_url, data=data)
        if r.status_code != 200:
            self.logger.error("\"%s\" can't connect" % delete_engine_url)
            return

        response = r.json()

        if "code" in response:
            self.logger.error(response["msg"])
            return

        self.logger.response("delete %s successfully" % image_name)

    def get_delete_engine_url(self):
        delete_engine_url = "%s/v1/rm" % self.configs.get("index", "kindo.cycore.cn")

        if delete_engine_url[:7].lower() != "http://" and delete_engine_url[:8].lower() != "https://":
            delete_engine_url = "http://%s" % delete_engine_url

        return delete_engine_url
