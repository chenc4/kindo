#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import traceback
from fabric.state import output
from fabric.tasks import execute
from fabric.api import env, prompt, settings, hide
from kindo.kindo_core import KindoCore
from kindo.utils.config_parser import ConfigParser
from kindo.commands.run_command import RunCommand


class ShellModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

        env.colorize_errors = False
        env.disable_colors = True
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
        if env.passwords is None or len(env.passwords) == 0:
            try:
                host = prompt("please input host: ", default="")
                if not host:
                    self.logger.error("hosts not found")
                    return

                host = "%s:22" % host if host is not None and host.rfind(":") == -1 else host
                host = "root@%s" % host if host is not None and host.rfind("@") == -1 else host

                pwd = prompt("please input password: ", default="")
                if not pwd:
                    self.logger.error("passowrds not found")
                    return

                env.passwords[host] = pwd
            except KeyboardInterrupt as e:
                pass
            except:
                self.logger.debug(traceback.format_exc())

        try:
            cmds = self.options[2:]

            cmd_infos = []
            for cmd in cmds:
                cmd_infos.append({"action": "RUN", "args": {"command": cmd}})

            execute(
                self.execute_script_commands,
                commands=cmd_infos,
                hosts=env.passwords.keys()
            )

        except KeyboardInterrupt as e:
            pass
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e)

    def execute_script_commands(self, commands):
        position = "~"
        envs = {}

        while True:
            for command in commands:
                with settings(hide('stderr', 'warnings'), warn_only=True):
                    position, envs = self.runCommand.run(
                        command=command,
                        filesdir=None,
                        imagesdir=None,
                        position=position,
                        envs=envs,
                        ki_path=None
                    )

            if len(self.options[2:]) > 0:
                return

            cmd = prompt("[%s@%s %s]# " % (env.user, env.host, position), default="")
            if cmd:
                commands = [{"action": "RUN", "args": {"command": cmd}}]

    def get_hosts_setting(self):
        ini_path = os.path.join(self.kindo_settings_path, "hosts.ini")
        if not os.path.isfile(ini_path):
            return {}

        cf = ConfigParser(ini_path)
        infos = cf.get()

        hosts = {}
        for section in infos:
            items = infos[section]
            section = section.lower()

            hosts[section] = {}
            for host in items:
                host = host.strip()
                password = items[host].strip()

                host = "%s:22" % host if host is not None and host.rfind(":") == -1 else host
                host = "root@%s" % host if host is not None and host.rfind("@") == -1 else host

                hosts[section][host] = password
        return hosts
