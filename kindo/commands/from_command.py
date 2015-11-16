#!/usr/bin/env python
#-*- coding: utf-8 -*-

import re
import os
import requests

from fabric.api import cd, prompt
from fabric.context_managers import shell_env

from kindo import KINDO_DEFAULT_HUB_HOST
from kindo.commands.command import Command


class FromCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value):
        value = value.strip()[5:]

        if not value:
            return {}

        image_info = self._pull_image_info(self._get_pull_engine_url(), value)

        while True:
            if "code" not in image_info:
                break

            code = prompt("please input the extraction code: ")
            if not code:
                return {}

            image_info = self._pull_image_info(self._get_pull_engine_url(), value, {"code": code})

        return {
            "action": "FROM",
            "args": {"url": image_info["url"], "name": image_info["name"]},
            "files": [],
            "images": [{"url": image_info["url"], "name": image_info["name"]}]
        }

    def run(self, command, depsdir, position, envs):
        
        return 1, position, "", envs

    def _get_pull_engine_url(self):
        pull_engine_url = "%s/v1/pull" % self.configs.get("index", KINDO_DEFAULT_HUB_HOST)

        if pull_engine_url[:7].lower() != "http://" and pull_engine_url[:8].lower() != "https://":
            pull_engine_url = "http://%s" % pull_engine_url

        return pull_engine_url

    def _pull_image_info(self, pull_engine_url, image_name, params=None):
        name, version = image_name.split(":") if ":"in image_name else (image_name, "")
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
            raise Exception("{0} can't connect".format(pull_engine_url))

        return r.json()