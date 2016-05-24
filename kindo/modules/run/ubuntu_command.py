#!/usr/bin/env python
#-*- coding: utf-8 -*-
import simplejson
from kindo.modules.run.command import Command


class UbuntuCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value, kic_path=None):
        command_str = value[7:].strip()
        if not command_str:
            return {}

        try:
            if command_str[0] == "[" and command_str[-1] == "]":
                command_list = simplejson.loads(command_str.replace("\\", "\\\\"))
                command_str = " ".join(command_list)
        except:
            pass

        return {
            "action": "UBUNTU",
            "args": {"command": command_str},
            "files": [],
            "images": []
        }

    def run(self, ssh_client, command, filesdir, imagesdir, cd, envs, ki_path=None):
        stdouts, stderrs, status = ssh_client.sudo("head -n 1 /etc/issue")
        if status > 0:
            raise Exception(" ".join(stderrs))

        if "Ubuntu" in stdouts[0]:
            stdouts, stderrs, status = ssh_client.sudo(command["args"]["command"], cd, envs)
            if status > 0:
                raise Exception(" ".join(stderrs))
        return cd, envs
