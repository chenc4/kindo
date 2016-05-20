#!/usr/bin/env python
#-*- coding: utf-8 -*-

import re
import traceback
from kindo.utils.functions import prompt
from kindo.kindo_core import KindoCore


class LoginModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

    def start(self):
        username = ""
        password = ""

        if len(self.options) <= 2:
            username = prompt("please input the username:", default="").strip()
        else:
            username = self.options[2]

        if not username or len(re.findall("[^a-zA-Z0-9]", username)) > 0:
            self.logger.error("username invalid", False)
            return

        if len(self.options) <= 3:
            password = prompt("please input the password:", default="").strip()
        else:
            password = self.options[3]

        if not password:
            self.logger.error("invalid password", False)
            return

        try:
            isok, res = self.api.login(username, password)
            if not isok:
                self.logger.error(res)
                return

            self.set_kindo_setting("username", username)
            self.set_kindo_setting("password", password)

            self.logger.info("login successfully")
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e)
