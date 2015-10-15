#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import hashlib
import traceback
import requests
from ..utils.configParser import ConfigParser
from ..core.kindoCore import KindoCore


class RmModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        if len(self.options) < 3:
            self.logger.response("no images", False)
            return

        self.logger.debug(self.options)

        try:
            self.delete_image(self.options[2])
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.response(e, False)

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

        self.logger.debug("connecting %s" % delete_engine_url)

        r = requests.post(delete_engine_url, data=data)
        if r.status_code != 200:
            raise Exception("\"%s\" can't connect" % delete_engine_url)

        response = r.json()

        if "code" in response:
            raise Exception(response["msg"])

        self.logger.response("delete %s successfully" % image_name)

    def get_delete_engine_url(self):
        delete_engine_url = "%s/v1/rm" % self.configs.get("index", "kindo.cycore.cn")

        if delete_engine_url[:7].lower() != "http://" and delete_engine_url[:8].lower() != "https://":
            delete_engine_url = "http://%s" % delete_engine_url

        return delete_engine_url
