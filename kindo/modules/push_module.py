#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import uuid
import traceback
import hashlib
import simplejson
from kindo.kindo_core import KindoCore
from kindo.utils.config_parser import ConfigParser
from kindo.utils.functions import unzip_to_folder


class PushModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        try:
            for option in self.options[2:]:
                ki_path = self.get_ki_path(option)
                if not ki_path or not os.path.isfile(ki_path):
                    raise Exception("\"%s\" not found" % option)

                self.logger.debug("pushing %s" % option)

                data = {
                    "username": self.configs.get("default", {}).get("username", ""),
                    "token": hashlib.new("md5", self.configs.get("default", {}).get("password", "").encode("utf-8")).hexdigest()
                }

                cache_folder = os.path.join(self.kindo_caches_path, str(uuid.uuid4()))
                if not unzip_to_folder(ki_path, cache_folder, "manifest.json"):
                    raise Exception("unpackage failed: %s" % ki_path)

                manifest_path = os.path.join(cache_folder, "manifest.json")
                if not os.path.isfile(manifest_path):
                    raise Exception("unpackage failed: %s" % ki_path)

                with open(manifest_path, "r") as fs:
                    manifest = simplejson.load(fs)
                    data["name"] = manifest.get("name", "")
                    data["author"] = data["username"]
                    data["version"] = manifest.get("version", "latest")
                    data["homepage"] = manifest.get("homepage", "")
                    data["platform"] = manifest.get("platform", "")
                    data["website"] = manifest.get("website", "")
                    data["summary"] = manifest.get("summary", "")
                    data["license"] = manifest.get("license", "")
                    data["buildversion"] = manifest.get("build_version", "")
                    data["buildtime"] = manifest.get("build_time", "")

                isok, res = self.api.push(ki_path, data)
                if not isok:
                    self.logger.error(res)
                    return

                self.logger.info("push ok")
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e)

    def get_ki_path(self, name):
        kiname = name if name[-3:] == ".ki" else "%s.ki" % name
        self.logger.debug("finding %s" % kiname)
        if os.path.isfile(kiname):
            self.logger.debug("finded %s" % kiname)
            return kiname

        path = os.path.realpath(kiname)
        self.logger.debug("finding %s" % path)
        if os.path.isfile(path):
            self.logger.debug("finded %s" % path)
            return path

        path = os.path.join(self.startfolder, kiname)
        self.logger.debug("finding %s" % path)
        if os.path.isfile(path):
            self.logger.debug("finded %s" % path)
            return path

        path = self.get_image_path(name)
        self.logger.debug("finding %s" % path)
        if os.path.isfile(path):
            self.logger.debug("finded %s" % path)
            return path

        return ""

    def get_image_path(self, section):
        ini_path = os.path.join(self.kindo_settings_path, "images.ini")
        if not os.path.isfile(ini_path):
            return ""

        cf = ConfigParser(ini_path)

        infos = cf.get()
        if section not in infos:
            return ""

        if "path" not in infos[section]:
            return ""
        return infos[section]["path"]
