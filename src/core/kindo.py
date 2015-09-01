#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys
import tempfile
import traceback
import tarfile
from utils.argsParser import ArgsParser
from utils.logger import Logger
from core.run import RunCommand
from core.build import Build
from core.search import Search
from core.clean import Clean
from core.register import Register
from core.commit import Commit

class Kindo:
    def __init__(self, startfolder, argv):
        self.startfolder = startfolder
        self.argv = argv
        self.options, self.configs = ArgsParse(self.argv).parse_args()

        logs_path = "/var/log/kindo" if os.path.isdir("/var/log") else os.path.join(self.startfolder, "logs")
        is_debug = True if "d" in self.configs else False

        self.logger = Logger(logs_path, is_debug)

        self.core_commands = {
            "run": RunCommand,
            "build": Build,
            "search": Search,
            "clean": Clean,
            "register": Register,
            "commit": Commit
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
                command,
                self.startfolder,
                self.configs,
                self.options,
                self.logger
            )

            core_command_cls.start()
        except:
            self.logger.debug(traceback.format_exc())
            self.logger.error("KINDO RUN ERROR")

    def show_help(self):
        banner = """Usage: kindo [options]
search:
    kindo search [package/conf name]

build:
    kindo build [.kic] -o [outfolder]
    or
    kindo [.kic] -o [outfolder]

run:
    kindo run [.ki] -h [account@host:port] -p [password] --[varible]=[value]
    or
    kindo run [.ki] -h [account@host:port] -p [password] --[varible]=[value]

clean:
    kindo clean

register:
    kindo register [name] [password]

commit:
    kindo commit [package / conf path]
"""
        self.logger.response(banner)

def run():
    startfolder = os.path.dirname(sys.executable)
    if sys.argv[0][-3:] == ".py":
        startfolder = os.path.dirname(os.path.realpath(sys.argv[0]))

    kindo = Kindo(startfolder, sys.argv)
    kindo.start()

if __name__ == '__main__':
    run()
