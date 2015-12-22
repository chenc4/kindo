#!/usr/bin/env python
#-*- coding: utf-8 -*-
from kindo.commands.command import Command


class MaintainerCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value, kic_path=None):
        if not value[10:]:
            return {}

        return {
            "action": "MAINTAINER",
            "args": {"value": value[10:]},
            "images": [],
            "files": []
        }

    def run(self, command, filesdir, imagesdir, position, envs, ki_path=None):
        banner = u"""　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
，，，　，，，　，，，，　，，，，　，，，，　，，，，，　　　，，，，　　　　
　，　，，　　　　　，　　　　，，，　　，　　　，　　，，　，，　　，，　　　
　，，，　　　　　　，　　　　，，，，　，　　　，　　，，　，，　　，，　　　
　，，，　　　　　　，　　　　，　，，　，　　　，　　　，　，　　　　，　　　
　，　，，　　　　　，　　　　，　　，，，　　　，　　，，　，，　　，，　　　
　，　，，，　　　　，　　　　，　　　，，　　　，　　，，　，，　　，，　　　
，，，，，，，　，，，，　　，，，　　，，　　，，，，，　　　，，，，　　　　

                    MAINTAINER:     %s
""" % command["args"]["value"]

        self.logger.info(banner)
        return position, envs
