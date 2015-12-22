#!/usr/bin/env python
#-*- coding: utf-8 -*-

import re
import requests
import hashlib
import traceback
from fabric.operations import prompt
from kindo.kindo_core import KindoCore


class LoginModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        login_engine_url = self.get_login_engine_url()

        username = ""
        password = ""

        if len(self.options) <= 2:
            username = prompt("please input the username:", default="").strip()
        else:
            username = self.options[2]

        if not username or len(re.findall("[^a-zA-Z0-9]", username)) > 0:
            self.logger.response("username invalid", False)
            return

        if len(self.options) <= 3:
            password = prompt("please input the password:", default="").strip()
        else:
            password = self.options[3]

        if not password:
            self.logger.response("invalid password", False)
            return

        try:
            self.logger.debug("connecting %s" % login_engine_url)
            r = requests.post(
                login_engine_url,
                data={
                    "username": username,
                    "token": hashlib.new("md5", password).hexdigest()
                }
            )
            if r.status_code != 200:
                raise Exception("\"%s\" can't connect" % login_engine_url)

            response = r.json()

            if "code" in response:
                self.logger.error(response["msg"])
                return

            if "username" not in response:
                self.logger.error("login failed")
                return

            self.set_kindo_setting("username", username)
            self.set_kindo_setting("password", password)

            self.logger.response("login successfully")
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.response(e, False)

    def get_login_engine_url(self):
        login_engine_url = "%s/v1/login" % self.configs.get("index", self.kind_default_hub_host)

        if login_engine_url[:7].lower() != "http://" and login_engine_url[:8].lower() != "https://":
            login_engine_url = "http://%s" % login_engine_url

        return login_engine_url
