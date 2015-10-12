#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
from fabric.state import output
from fabric.tasks import execute
from fabric.api import env
from utils.configParser import ConfigParser
from core.kindoCore import KindoCore
from commands.runCommand import RunCommand


class ShellModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

        env.colorize_errors = True
        env.command_timeout = self.configs.get("timout", 60 * 30)
        env.output_prefix = ""
        env.passwords = {}
        output.debug = False
        output.running = False

        host = configs.get("h", None)
        host = "%s:22" % host if host is not None and host.rfind(":") == -1 else host
        host = "root@%s" % host if host is not None and host.rfind("@") == -1 else host

        password = configs.get("p", "")

        if host is not None:
            env.passwords[host] = password

        hosts = self.get_hosts_setting()

        groups = configs["g"].split(",") if "g" in configs else []
        for group in groups:
            group = group.strip()

            if group not in hosts:
                self.logger.warn("GROUP NOT FOUND: %s" % group)
                continue

            for k, v in hosts[group].items():
                env.passwords[k] = v

        if len(env.passwords) == 0 and "default" in hosts:
            for k, v in hosts["default"].items():
                env.passwords[k] = v

        self.runCommand = RunCommand(startfolder, configs, options, logger)

    def start(self):
        if len(self.options) <= 2:
            self.logger.response("no shell command", False)
            return

        if env.passwords is None or len(env.passwords) == 0:
            self.logger.response("hosts not found", False)
            return

        try:
            for option in self.options[2:]:
                execute(
                    self.execute_script_commands,
                    commands=[{"action": "RUN", "args": {"command": option}, "variables": []}],
                    hosts=env.passwords.keys()
                )
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.response(e, False)

    def execute_script_commands(self, commands):
        position = "~"
        for command in commands:
            if "action" not in command:
                raise Exception("command invalid")

            status, position, errormsg = self.runCommand.run(command, None, position)
            # if the command is executed(success or fail), not continue
            if status == 0:
                self.logger.debug(errormsg)

    def get_hosts_setting(self):
        ini_path = os.path.join(self.kindo_settings_path, "hosts.ini")
        if not os.path.isfile(ini_path):
            return {}

        cf = ConfigParser()
        cf.read(ini_path)

        hosts = {}
        for section in cf.sections():
            items = cf.items(section)
            section = section.lower()

            hosts[section] = {}
            for host, password in items:
                host = host.strip()
                password = password.strip()

                host = "%s:22" % host if host is not None and host.rfind(":") == -1 else host
                host = "root@%s" % host if host is not None and host.rfind("@") == -1 else host

                hosts[section][host] = password
        return hosts
