#!/usr/bin/env python
#-*- coding: utf-8 -*-

from ..core.kindoCore import KindoCore


class HelpModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

        self.commands_info = {
            "build": {
                "description": "Build an image from the kicfile",
                "command": "kindo build [kic path]",
                "options": {
                    "-d": "Enable debug information",
                    "-o": "Specify the output folder",
                    "-t": "set the image tag, for example: author/name:version",
                    "--kipwd": "set unpackage password"
                }
            },
            "commit": {
                "description": "Commit local image to the image's path",
                "command": "kindo commit [ki path]",
                "options": {
                    "-d": "Enable debug information",
                    "-t": "set the image tag, for example: author/name:version"
                }
            },
            "clean": {
                "description": "Clean the local caches",
                "command": "kindo clean",
                "options": {
                    "-d": "Enable debug information"
                }
            },
            "help": {
                "description": "Show the command options",
                "command": "kindo help [kindo command name]",
                "options": {
                    "-d": "Enable debug information"
                }
            },
            "images": {
                "description": "List local images",
                "command": "kindo images",
                "options": {
                    "-d": "Enable debug information"
                }
            },
            "info": {
                "description": "Display system-wide information",
                "command": "kindo info",
                "options": {
                    "-d": "Enable debug information"
                }
            },
            "login": {
                "description": "account login, set account info automatically",
                "command": "kindo login [username] [password]",
                "options": {
                    "-d": "Enable debug information"
                }
            },
            "logout": {
                "description": "account logout, clean account info automatically",
                "command": "kindo logout",
                "options": {
                    "-d": "Enable debug information"
                }
            },
            "pull": {
                "description": "Pull an image from the kindo hub",
                "command": "kindo pull [author/name:version]",
                "options": {
                    "-d": "Enable debug information",
                    "--code": "Set the extraction code, only six characters are allowed"
                }
            },
            "push": {
                "description": "Push an image to the kindo hub",
                "command": "kindo push [ki image path|ki image name]",
                "options": {
                    "-d": "Enable debug information",
                    "--code": "Set the extraction code, only six characters are allowed"
                }
            },
            "register": {
                "description": "Register the kindo hub's account",
                "command": "kindo register",
                "options": {
                    "-d": "Enable debug information"
                }
            },
            "rm": {
                "description": "Delete the owned image in the kindo hub",
                "command": "kindo rm [author/name:version]",
                "options": {
                    "-d": "Enable debug information"
                }
            },
            "rmi": {
                "description": "Remove one or more local images",
                "command": "kindo rmi [author/name:version]",
                "options": {
                    "-d": "Enable debug information"
                }
            },
            "run": {
                "description": "Run image commands to the target operating system",
                "command": "kindo run [ki image path|ki image name]",
                "options": {
                    "-d": "Enable debug information",
                    "-h": "host, for example: account@ip:port",
                    "-p": "account password",
                    "-g": "set the hosts group name",
                    "--kipwd": "set unpackage password"
                }
            },
            "search": {
                "description": "Search an image on the kindo hub",
                "command": "kindo search [image name]",
                "options": {
                    "-d": "Enable debug information"
                }
            },
            "version": {
                "description": "Show the kindo information",
                "command": "kindo version",
                "options": {
                    "-d": "Enable debug information"
                }
            }
        }

    def start(self):
        if len(self.options) < 3:
            self.show_all_kindo_commands_options()
            return

        self.show_kindo_command_options(self.options[2])

    def show_all_kindo_commands_options(self):
       for name, command_info in self.commands_info.items():
            info = """
%s:
    %s

    command:
        %s

    options:
""" % (name, command_info["description"], command_info["command"])
            for k, v in command_info["options"].items():
                info += """
       %s      %s""" % (k, v)
            self.logger.info(info)

    def show_kindo_command_options(self, name):
        name = name.lower()
        if name not in self.commands_info:
            return

        info = """
%s:
    %s

    command:
        %s

    options:
""" % (name, self.commands_info[name]["description"], self.commands_info[name]["command"])

        for k, v in self.commands_info[name]["options"].items():
            info += """
       %s      %s""" % (k, v)
        self.logger.info(info)
