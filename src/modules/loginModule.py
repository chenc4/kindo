#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import re
import requests
import hashlib
import traceback
from fabric.operations import prompt
from utils.configParser import ConfigParser
from modules.kindoModule import KindoModule


class LoginModule(KindoModule):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoModule.__init__(self, command, startfolder, configs, options, logger)

    def start(self):
        login_engine_url = self.get_login_engine_url()

        username = ""
        password = ""

        if len(self.options) <= 2:
            username = prompt("please input the username:", default="").strip()
        else:
            username = self.options[2]

        if not username or len(re.findall("[^a-zA-Z0-9]", username)) > 0:
            self.logger.error("username invalid")
            return

        if len(self.options) <= 3:
            password = prompt("please input the password:", default="").strip()
        else:
            password = self.options[3]

        if not password:
            self.logger.error("invalid password")
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
                self.logger.error("\"%s\" can't connect" % login_engine_url)
                return

            response = r.json()

            if "code" in response:
                self.logger.error(response["msg"])
                return

            if "username" not in response:
                self.logger.error("login failed")
                return

            self.set_kindo_setting("username", username)
            self.set_kindo_setting("password", password)

            self.logger.info("login successfully")
        except:
            self.logger.debug(traceback.format_exc())
            self.logger.error("login failed")

    def get_login_engine_url(self):
        login_engine_url = "%s/v1/login" % self.configs.get("index", "kindo.cycore.cn")

        if login_engine_url[:7].lower() != "http://" and login_engine_url[:8].lower() != "https://":
            login_engine_url = "http://%s" % login_engine_url

        return login_engine_url
