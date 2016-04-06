#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import simplejson

try:
    import urlparse
except:
    from urllib.parse import urlparse

from fabric.api import cd
from fabric.context_managers import shell_env
from kindo.commands.command import Command
from kindo.utils.functions import get_files_info, get_content_parts


class AddCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value, kic_path=None):
        command_value = value[4:].strip()
        if not command_value:
            return {}

        paths = []
        if command_value[0] == "[" and command_value[-1] == "]":
            try:
                paths = simplejson.loads(command_value.replace("\\", "\\\\"))
            except:
                raise Exception("invalid json array")

        if not paths:
            # if path has whitespace, quote it. and support multi paths
            paths = get_content_parts(command_value)

        if len(paths) == 1:
            raise Exception("target not found")

        args = []
        files = []

        for path in paths[:-1]:
            # the <src> allow remote file URL
            if "http://" in path or "https://" in path:
                urlinfo = urlparse.urlparse(path)
                filename = os.path.split(urlinfo["path"])[1]

                if (
                    ":" in filename or
                    "?" in filename or
                    "*" in filename or
                    "\"" in filename or
                    "<" in filename or
                    ">" in filename or
                    "/" in filename or
                    "\\" in filename or
                    "|" in filename
                ):
                    raise Exception("the filename has special character")

                files.append(
                    {"name": filename, "url": path}
                )

                # if <dest> ends with a trailing slash /, it will be considered a directory
                if paths[-1][-1] == "/":
                    to = "%s%s" % (paths[-1], filename)
                    args.append({"from": filename, "to": to})
                else:
                    args.append({"from": filename, "to": paths[-1]})
                continue

            if not os.path.isdir(path) and not os.path.isfile(path):
                kic_folder = os.path.dirname(kic_path)
                path = os.path.join(kic_folder, path)

            if not os.path.exists(path):
                raise Exception("%s not found" % path)

            # the <src> allow directory
            if os.path.isdir(path):
                files_info = get_files_info(path)

                files.extend(files_info)

                for file_info in files_info:
                    # if <dest> ends with a trailing slash /, it will be considered a directory
                    if paths[-1][-1] == "/":
                        to = "%s%s" % (paths[-1], file_info["name"])
                        args.append({"from": file_info["name"], "to": to})
                    elif len(files_info) > 1:
                        to = "%s/%s" % (paths[-1], file_info["name"])
                        args.append({"from": file_info["name"], "to": to})
                    else:
                        args.append({"from": file_info["name"], "to": paths[-1]})
            elif os.path.isfile(path):
                filedir, filename = os.path.split(path)
                files.append(
                    {"name": filename, "url": path}
                )

                # if <dest> ends with a trailing slash /, it will be considered a directory
                if paths[-1][-1] == "/":
                    to = "%s%s" % (paths[-1], filename)
                    args.append({"from": filename, "to": to})
                elif len(paths) > 2:
                    to = "%s/%s" % (paths[-1], filename)
                    args.append({"from": filename, "to": to})
                else:
                    args.append({"from": filename, "to": paths[-1]})

        return {
            "action": "ADD",
            "args": args,
            "images": [],
            "files": files
        }

    def run(self, command, filesdir, imagesdir, position, envs, ki_path=None):
        if not command["args"]:
            return position, envs

        args = []
        if isinstance(command["args"], dict):
            args = [command["args"]]
        elif isinstance(command["args"], list):
            args = command["args"]

        for arg in args:
            src = os.path.join(filesdir, arg["from"])
            if not os.path.isfile(src):
                raise Exception("{0} not found".format(src))

            with cd(position):
                with shell_env(**envs):
                    if not self.upload(src, arg["to"]):
                        raise Exception("{0} upload failed".format(src))
                    return position, envs
        return position, envs
