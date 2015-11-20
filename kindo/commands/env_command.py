#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import os
from fabric.api import cd
from kindo.commands.command import Command
from kindo.utils.functions import get_content_parts


class EnvCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value, kic_path=None):
        args = []
        value = value[4:].strip()
        if "=" in value:
            args = self._parse_env_value(value)
        else:
            first_space_pos = value.find(" ")
            env_key = value[:first_space_pos].strip("\"")
            env_value = value[first_space_pos + 1:].strip().strip("\"")

            if len(re.findall("[^\w_]", env_key)) > 0:
                raise Exception("invalid env variable name")

            args.append({"key": env_key, "value": env_value})

        if not args:
            return {}

        return {
            "action": "ENV",
            "args": args,
            "variables": [],
            "files": []
        }

    def run(self, command, filesdir, imagesdir, position, envs, ki_path=None):
        # old kic didn't support that the command type is list
        if isinstance(command["args"], list):
            for c in command["args"]:
                envs[c["key"]] = c["value"]
        elif isinstance(command["args"], dict):
            envs[command["args"]["key"]] = command["args"]["value"]

        return position, envs

    def _parse_env_value(self, content):
        has_backslashes = True if "\ " in content else False
        parts = get_content_parts(content if not has_backslashes else content.replace("\ ", "/_\\"))

        envs = []
        last_key = None

        for part in parts:
            if part == "=":
                continue

            if last_key is None:
                if part[-1] == "=":
                    last_key = part[:-1]

                elif part[0] == "=":
                    last_key = part
                elif "=" in part:
                    first_equal_pos = part.find("=")
                    if len(re.findall("[^\w_]", part[:first_equal_pos])) > 0:
                        raise Exception("invalid env variable name")

                    v = part[first_equal_pos + 1:]
                    if has_backslashes and "/_\\" in v:
                        v = v.replace("/_\\", " ")
                    envs.append(
                        {
                            "key": part[:first_equal_pos],
                            "value": v
                        }
                    )
                else:
                    last_key = part
            else:
                if len(re.findall("[^\w_]", last_key)) > 0:
                    raise Exception("invalid env variable name")

                # support backslashes
                if has_backslashes and "/_\\" in part:
                    part = part.replace("/_\\", " ")
                envs.append(
                    {
                        "key": last_key,
                        "value": part
                    }
                )
                last_key = None
        return envs




