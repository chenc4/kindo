#!/usr/bin/env python
#-*- coding: utf-8 -*-

import re
import traceback
from kindo.utils.functions import prompt
from kindo.kindo_core import KindoCore


class RegisterModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
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

            isok, res = self.api.register(username, password)
            if not isok:
                self.logger.error(res)
                return

            self.set_kindo_setting("username", username)
            self.set_kindo_setting("password", password)

            self.logger.info("registered")
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e)
