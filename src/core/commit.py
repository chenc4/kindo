#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import traceback
import requests
from core.kindoCore import KindoCore


class Commit(KindoCore):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoCore.__init__(self, command, startfolder, configs, options, logger)

    def start(self):
        commit_engine_url = "%s/v1/commit" % self.configs.get("index", "kindo.cycore.cn")
        if commit_engine_url[:7].lower() != "http://" and commit_engine_url[:8].lower() != "https://":
            commit_engine_url = "http://%s" % commit_engine_url

        for option in self.options[2:]:
            try:
                if option[-3:].lower() != ".ki":
                    self.logger.warn("INVALID KI PACKAGE: %s" % option)
                    continue

                package_path = self.get_package_path(option)
                if not package_path or not os.path.isfile(package_path):
                    self.logger.warn("\"%s\" not found" % option)
                    continue

                self.logger.info("commiting %s" % option)

                data = {}
                if "username" in self.configs:
                    data["username"] = self.configs["username"]

                if "password" in self.configs:
                    data["token"] = hashlib.new("md5", self.configs["password"]).hexdigest()

                self.logger.info("connecting %s" % commit_engine_url)
                r = requests.post(commit_engine_url, data=data, files={"file": package_path})
                if r.status_code != 200:
                    self.logger.error("\"%s\" can't connect" % commit_engine_url)
                    return

                response = r.json()

                if "code" in response:
                    self.logger.error(response["msg"])
                    return

                self.logger.response("commited %s" % option)
            except:
                self.logger.debug(traceback.format_exc())
                self.logger.error("\"%s\" can't connect" % commit_engine_url)

    def get_package_path(self, name):
        self.logger.info("finding %s" % name)
        if os.path.isfile(name):
            return name

        path = os.path.realpath(name)
        self.logger.info("finding %s" % path)
        if os.path.isfile(path):
            return path

        path = os.path.join(self.startfolder, name)
        self.logger.info("finding %s" % path)
        if os.path.isfile(path):
            return path

        path = os.path.join(self.startfolder, "packages", name)
        self.logger.info("finding %s" % path)
        if os.path.isfile(path):
            return path

        path = os.path.join(self.kindo_packages_path, name)
        self.logger.info("finding %s" % path)
        if os.path.isfile(path):
            return path

        return ""


