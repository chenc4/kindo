#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import getpass
import traceback
from kindo.kindo_core import KindoCore
from kindo.utils.config_parser import ConfigParser
from kindo.utils.functions import prompt, hostparse
from kindo.utils.kissh import KiSSHClient
from kindo.modules.run.run_command import RunCommand


class ShellModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

        host = self.configs.get("h", self.configs.get("host", "")).strip()
        password = self.configs.get("p", self.configs.get("password", "")).strip()
        group = self.configs.get("g", self.configs.get("group", "")).strip()

        host = "%s:22" % host if host is not None and host.rfind(":") == -1 else host
        host = "root@%s" % host if host is not None and host.rfind("@") == -1 else host

        hosts = self.get_hosts_setting()

        if group and group not in hosts:
            self.logger.warn("GROUP NOT FOUND: %s" % group)

        self.activate_hosts = []
        if host:
            host, port, username = hostparse(host)
            while not password:
                password = getpass.getpass("please input password: ")

            self.activate_hosts.append({
                "host": host,
                "port": port,
                "username": username,
                "password": password
            })

        if group in hosts:
            for k, v in hosts[group].items():
                host, port, username = hostparse(k)
                self.activate_hosts.append({
                    "host": host,
                    "port": port,
                    "username": username,
                    "password": v
                })

        self.runCommand = RunCommand(startfolder, configs, options, logger)

    def start(self):
        if len(self.activate_hosts) == 0:
            try:
                host = prompt("please input host: ", default="")
                if host is None or not host:
                    self.logger.error("hosts not found")
                    return

                port = 22
                username = "root"

                pos = host.rfind(":")
                if pos == -1:
                    host = host
                else:
                    host = host[:pos]
                    port = host[pos + 1:]

                pos = host.find("@")
                if pos != -1:
                    username = host[:pos]
                    host = host[pos + 1:]

                password = getpass.getpass("please input password: ")
                if not password:
                    self.logger.error("passowrds not found")
                    return

                self.activate_hosts.append({
                    "host": host,
                    "port": port,
                    "username": username,
                    "password": password
                })

            except KeyboardInterrupt as e:
                pass
            except:
                self.logger.debug(traceback.format_exc())

        if len(self.activate_hosts) > 1:
            self.logger.error("too many hosts")
            return

        try:
            self.execute(self.options[2:])
        except KeyboardInterrupt as e:
            pass
        except EOFError as e:
            pass
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e)

    def execute(self, commands):
        for activate_host in self.activate_hosts:
            with KiSSHClient(
                activate_host["host"],
                int(activate_host["port"]),
                activate_host["username"],
                activate_host["password"],
            ) as ssh_client:
                while True:
                    for command in commands:
                        stdouts, stderrs = ssh_client.execute(command)
                        for stdout in stdouts:
                            self.logger.info(stdout)

                        for stderr in stderrs:
                            self.logger.info(stderr)

                    commands = [prompt("[%s@%s:%s ~]# " % (activate_host["username"], activate_host["host"], activate_host["port"]), default="")]

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
