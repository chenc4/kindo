#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys
import tempfile
import traceback
import tarfile
from utils.argsParser import ArgsParser
from utils.logger import Logger
from modules.runModule import RunModule
from modules.buildModule import BuildModule
from modules.searchModule import SearchModule
from modules.shellModule import ShellModule
from modules.cleanModule import CleanModule
from modules.registerModule import RegisterModule
from modules.pushModule import PushModule
from modules.imagesModule import ImagesModule
from modules.rmiModule import RmiModule
from modules.infoModule import InfoModule
from modules.versionModule import VersionModule
from modules.helpModule import HelpModule
from modules.pullModule import PullModule
from modules.commitModule import CommitModule
from modules.logoutModule import LogoutModule
from modules.loginModule import LoginModule
from modules.rmModule import RmModule


class Kindo:
    def __init__(self, startfolder, argv):
        self.startfolder = startfolder
        self.argv = argv
        self.options, self.configs = ArgsParser(self.argv).parse_args()

        logs_path = "/var/log/kindo" if os.path.isdir("/var/log") else os.path.join(self.startfolder, "logs")
        is_debug = True if "d" in self.configs else False

        self.logger = Logger(logs_path, is_debug)

        self.core_commands = {
            "run": RunModule,
            "build": BuildModule,
            "search": SearchModule,
            "shell": ShellModule,
            "clean": CleanModule,
            "register": RegisterModule,
            "push": PushModule,
            "images": ImagesModule,
            "rm": RmModule,
            "rmi": RmiModule,
            "info": InfoModule,
            "login": LoginModule,
            "logout": LogoutModule,
            "version": VersionModule,
            "help": HelpModule,
            "pull": PullModule,
            "commit": CommitModule
        }

    def start(self):
        if len(self.argv) <= 1:
            self.show_help()
            return

        command = self.argv[1].lower()
        if command not in self.core_commands:
            ext = os.path.splitext(command)[1].lower()
            if ext not in [".kic", ".ki"]:
                self.show_help()
                return
            command = "build" if ext == ".kic" else "run"

        try:
            core_command_cls = self.core_commands[command](
                self.startfolder,
                self.configs,
                self.options,
                self.logger
            )

            core_command_cls.start()
        except KeyboardInterrupt as e:
            self.logger.warn("quit")
        except:
            self.logger.debug(traceback.format_exc())

    def show_help(self):
        banner = """a simple tool for packaging and deploying your codes
kindo commands:
    build       Build an image from the kicfile
    commit      Commit local image to the image's path
    clean       Clean the local caches
    help        Show the command options
    images      List local images
    info        Display system-wide information
    login       Account login
    logout      Account logout
    pull        Pull an image from the kindo hub
    push        Push an image to the kindo hub
    register    Register the kindo hub's account
    rm          Delete the owned image in the kindo hub
    rmi         Remove one or more local images
    run         Run image commands to the target operating system
    search      Search an image on the kindo hub
    shell       Execute shell command directly
    version     Show the kindo information

script commands:
    add        Add local or remote file to the target operating system
    addonrun   Add file or directory to the target operating system when running
    centos     Run an shell command on CentOS, others ignore
    check      Check whether the file or port existed or not
    download   Download file from the target operating system
    run        Run an shell command
    ubuntu     Run an shell command on Ubuntu, others ignore
    workdir    set the work directory when the shell command is running
"""
        self.logger.info(banner)

def run():
    startfolder = os.path.dirname(sys.executable)
    if sys.argv[0][-3:] == ".py":
        startfolder = os.path.dirname(os.path.realpath(sys.argv[0]))

    kindo = Kindo(startfolder, sys.argv)
    kindo.start()

if __name__ == '__main__':
    run()
