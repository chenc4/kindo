#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
try:
    import urlparse
except:
    from urllib.parse import urlparse
import simplejson
from fabric.api import cd
from fabric.context_managers import shell_env
from kindo.commands.command import Command
from kindo.utils.functions import download_with_progressbar, get_files_info, get_md5, get_content_parts


class AddOnRunCommand(Command):
    def __init__(self, startfolder, configs, options, logger):
        Command.__init__(self, startfolder, configs, options, logger)

    def parse(self, value, kic_path=None):
        command_value = value[9:].strip()
        if not command_value:
            return {}

        paths = []
        if command_value[0] == "[" and command_value[-1] == "]":
            try:
                paths = simplejson.loads(command_value.replace("\\", "/"))
            except:
                pass

        if not paths:
            # if path has whitespace, quote it. and support multi paths
            paths = get_content_parts(command_value)

        if len(paths) == 1:
            raise Exception("target not found")

        args = []

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

                # if <dest> ends with a trailing slash /, it will be considered a directory
                if paths[-1][-1] == "/":
                    to = "%s%s" % (paths[-1], filename)
                    args.append({"from": path, "to": to})
                elif len(paths) > 2:
                    to = "%s/%s" % (paths[-1], filename)
                    args.append({"from": path, "to": to})
                else:
                    args.append({"from": path, "to": paths[-1]})
                continue

            args.append({"from": path, "to": paths[-1]})

        return {
            "action": "ADDONRUN",
            "args": args,
            "images": [],
            "files": []
        }

    def run(self, command, filesdir, imagesdir, position, envs, ki_path=None):
        args = []

        if isinstance(command["args"], dict):
            args = [command["args"]]
        elif isinstance(command["args"], list):
            args = command["args"]

        files_info = []
        for arg in args:
            src = arg["from"]
            if "http://" in src or "https://" in src:
                urlinfo = urlparse.urlparse(src)
                filename = os.path.split(urlinfo["path"])[1]
                file_name, file_ext = os.path.splitext(filename)

                downloads_tmp_folder = os.path.join(self.kindo_tmps_path, "downloads")
                if not os.path.isdir(downloads_tmp_folder):
                    os.makedirs(downloads_tmp_folder)

                # create unique tmpfile
                src = os.path.join(downloads_tmp_folder, "%s%s" % (get_md5(arg["from"]), file_ext))
                if not os.path.isfile(src):
                    download_with_progressbar(arg["from"], src)
            elif not os.path.isdir(src) and not os.path.isfile(src):
                src = os.path.join(self.startfolder, arg["from"])

            if (
                not os.path.exists(src) and
                "http://" not in arg["from"] and
                "https://" not in arg["from"]
            ):
                ki_folder = os.path.dirname(ki_path)
                src = os.path.join(ki_folder, arg["from"])

            ignore = True if self.configs.get("ignore", 1) == 1 else False
            if not os.path.isfile(src) and not os.path.isdir(src):
                if ignore:
                    return position, envs
                raise Exception("{0} not found".format(src))

            if os.path.isfile(src):
                if arg["to"][-1] == "/":
                    filedir, filename = os.path.split(src)
                    files_info.append({
                        "from": src,
                        "to": "%s%s" % (arg["to"], filename)
                    })
                elif len(args) > 2:
                    filedir, filename = os.path.split(src)
                    files_info.append({
                        "from": src,
                        "to": "%s/%s" % (arg["to"], filename)
                    })
                else:
                    files_info.append({
                        "from": src,
                        "to": arg["to"]
                    })
            elif os.path.isdir(src):
                files = get_files_info(src)

                for f in files:
                    if arg["to"][-1] == "/":
                        files_info.append({
                            "from": f["url"],
                            "to": "%s%s" % (arg["to"], f["name"])
                        })
                    elif len(files) > 1:
                        files_info.append({
                            "from": f["url"],
                            "to": "%s/%s" % (arg["to"], f["name"])
                        })
                    else:
                        files_info.append({
                            "from": f["url"],
                            "to": arg["to"]
                        })

        with cd(position):
            with shell_env(**envs):
                for file_info in files_info:
                    if not self.upload(file_info["from"], file_info["to"]) and not ignore:
                        raise Exception("{0} upload failed".format(f))
        return position, envs
