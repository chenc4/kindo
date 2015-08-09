#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import sys
import tempfile
import tarfile
from parses.kicParse import KicParse
from parses.kiParse import KiParse
from utils.argsParse import ArgsParse
from utils.logger import Logger


class Kindo:
    def __init__(self, folder, argv):
        self.argv = argv
        self.skip = 1

        argsParse = ArgsParse(self.argv, self.skip)
        options, self.args = argsParse.parse_args()

        self.logger = Logger(os.path.join(folder, "logs"), self.args.get("d", False))

    def start(self):
        if len(self.argv) > 1:
            target = os.path.realpath(self.argv[1])
            ext = os.path.splitext(target)[1].lower()
            if os.path.isfile(target):
                if ext == ".kic":
                    parse = KicParse(target, self.args, self.logger)
                    parse.start()
                elif ext == ".ki":
                    parse = KiParse(target, self.args, self.logger)
                    parse.start()
        else:
            self.show_help()

    def show_help(self):
        banner = """Usage: kindo [options]

compile:
    kindo [.kic] -o [outfolder]

run:
    kindo [.ki] -h [account@host:port] -p [password] --[varible]=[value]
"""
        self.logger.info(banner)

def run():
    folder = os.path.dirname(sys.executable)
    if sys.argv[0][-3:] == ".py":
        folder = os.path.dirname(os.path.realpath(sys.argv[0]))

    kindo = Kindo(folder, sys.argv)
    kindo.start()    

if __name__ == '__main__':
    run()
