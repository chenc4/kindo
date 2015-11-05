#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import re
import requests
import traceback
from fabric.operations import prompt
from core.kindoCore import KindoCore


class RegisterModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        register_engine_url = "%s/v1/register" % self.configs.get("index", "kindo.cycore.cn")
        if register_engine_url[:7].lower() != "http://" and register_engine_url[:8].lower() != "https://":
            register_engine_url = "http://%s" % register_engine_url

        try:
            username = ""
            password = ""
            repassword = ""

            if len(self.options) <= 2:
                username = prompt("please input the username:", default="").strip()
            else:
                username = self.options[2]

            if not username or len(re.findall("[^a-zA-Z0-9]", username)) > 0:
                raise Exception("username invalid")

            if len(self.options) <= 3:
                password = prompt("please input the password:", default="").strip()
            else:
                password = self.options[3]

            if not password:
                raise Exception("invalid password")

            if len(self.options) <= 4:
                repassword = prompt("please input the password again:", default="").strip()

            if password != repassword:
                raise Exception("the passwords you typed do not match")

            self.logger.debug("connecting %s" % register_engine_url)
            r = requests.post(register_engine_url, data={"username": username, "password": password})
            if r.status_code != 200:
                raise Exception("\"%s\" can't connect" % register_engine_url)

            response = r.json()

            if "code" in response:
                raise Exception(response["msg"])

            self.set_kindo_setting("username", username)
            self.set_kindo_setting("password", password)

            self.logger.response("registered %s" % username)
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.response(e, False)
