#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import re
import time
import uuid
import tempfile
import traceback
import requests
import urlparse
import shutil
import pickle
import zipfile
import simplejson

from kindo.kindoCore import KindoCore
from kindo.utils.functions import download_with_progressbar
from kindo.commands.addCommand import AddCommand
from kindo.commands.checkCommand import CheckCommand
from kindo.commands.runCommand import RunCommand
from kindo.commands.workdirCommand import WorkdirCommand
from kindo.commands.downloadCommand import DownloadCommand
from kindo.commands.ubuntuCommand import UbuntuCommand
from kindo.commands.centosCommand import CentOSCommand
from kindo.commands.addOnRunCommand import AddOnRunCommand
from kindo.commands.envCommand import EnvCommand


class BuildModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

        self.kic_path_infos = []

        for option in options[2:]:
            filename, ext = os.path.splitext(option)
            if "." not in ext:
                ext = ".kic"
                option = "%s.kic" % option

            if ext.lower() != ".kic":
                continue

            kic_path, outfolder = self.get_kic_info(option)
            if kic_path is None or not kic_path:
                self.logger.debug("kic not found: %s" % option)
                continue

            self.kic_path_infos.append(
                {
                    "path": kic_path,
                    "outfolder": outfolder
                }
            )

        self.handlers = {
            "add": AddCommand(startfolder, configs, options, logger),
            "check": CheckCommand(startfolder, configs, options, logger),
            "run": RunCommand(startfolder, configs, options, logger),
            "workdir": WorkdirCommand(startfolder, configs, options, logger),
            "download": DownloadCommand(startfolder, configs, options, logger),
            "ubuntu": UbuntuCommand(startfolder, configs, options, logger),
            "centos": CentOSCommand(startfolder, configs, options, logger),
            "addonrun": AddOnRunCommand(startfolder, configs, options, logger),
            "env": EnvCommand(startfolder, configs, options, logger)
        }

        self.re_pattern =  "^\s*(%s)\s+" % "|".join(self.handlers.keys())

    def start(self):
        try:
            if not self.kic_path_infos:
                self.logger.error("no kics")
                return

            for kic_path_info in self.kic_path_infos:
                if not os.path.isdir(kic_path_info["outfolder"]):
                    os.makedirs(kic_path_info["outfolder"])

                kic_build_folder = os.path.join(self.kindo_tmps_path, uuid.uuid4().hex)
                if not os.path.isdir(kic_build_folder):
                    kic_build_sub_folders = [
                        os.path.join(kic_build_folder, "kics"),
                        os.path.join(kic_build_folder, "files"),
                        os.path.join(kic_build_folder, "deps")
                    ]
                    for kic_build_sub_folder in kic_build_sub_folders:
                        os.makedirs(kic_build_sub_folder)

                try:
                    commands, author, version, website, name, summary, license, platform = self.build_kic(
                        kic_path_info["path"], kic_build_folder
                    )

                    if len(re.findall("[^a-zA-Z0-9]", author)) > 0:
                        raise Exception("invalid author name, just allow 'a-zA-Z0-9-_'")

                    if len(re.findall("[^a-zA-Z0-9-_]", name)) > 0:
                        raise Exception("invalid name, just allow 'a-zA-Z0-9-_'")

                    if len(re.findall("[^a-zA-Z0-9\.-]", version)) > 0:
                        raise Exception("invalid version, just allow 'a-zA-Z0-9\.-'")

                    if (
                        len(re.findall("^[a-zA-Z]+(/x86)?$", platform)) <= 0 and
                        len(re.findall("^[a-zA-Z]+(/x64)?$", platform)) <= 0
                    ):
                        raise Exception("invalid platform, just allow '[os]/x86 or [os]/x64'")

                    shutil.copy(
                        kic_path_info["path"],
                        os.path.join(
                            kic_build_folder,
                            "kics",
                            "%s-%s-%s.kic" % (author, name, version)
                        )
                    )

                    files = []
                    deps = []
                    for c in commands:
                        if "files" in c:
                            files += self.put_files_to_build_path(
                                c["files"],
                                kic_build_folder,
                                kic_path_info["path"]
                            )

                        if "deps" in c:
                            deps += self.put_deps_to_build_path(
                                c["deps"],
                                kic_build_folder
                            )

                    manifest_json = {
                        "name": name,
                        "version": version,
                        "author": author,
                        "website": website,
                        "summary": summary,
                        "license": license,
                        "platform": platform,
                        "build_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        "build_version": 3,
                        "build_os": "",
                        "run_min_version": 1,
                        "files": files,
                        "deps": deps
                    }

                    manifest = os.path.join(kic_build_folder, "manifest.json")
                    with open(manifest, 'wb') as fs:
                        simplejson.dump(manifest_json, fs)

                    output_ki_path = self.configs.get(
                        "o",
                        kic_path_info["outfolder"]
                    )

                    if output_ki_path[-3:].lower() != ".ki":
                        output_ki_path = os.path.join(output_ki_path, "%s-%s-%s.ki" % (author, name, version))

                    output_ki_dir = os.path.dirname(output_ki_path)
                    if not os.path.isdir(output_ki_dir):
                        os.makedirs(output_ki_dir)

                    self.logger.debug("packaging %s" % output_ki_path)
                    self.zip_dir(kic_build_folder, output_ki_path)
                    self.logger.debug("packaged %s" % output_ki_path)
                except Exception as e:
                    self.logger.debug(traceback.format_exc())
                    return
                finally:
                    shutil.rmtree(kic_build_folder)
                self.logger.response("build ok: %s" % kic_path_info["path"])
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e)


    def put_files_to_build_path(self, files, kic_build_folder, kic_path):
        filenames = []
        for f in files:
            filename = re.sub("[\?|\+|\*|\<|\>|:]", "", os.path.split(f)[1])
            filenames.append(filename)

            target = os.path.join(kic_build_folder, "files", filename)
            if f[:7].lower() == "http://" or f[:8].lower() == "https://":
                download_with_progressbar(f, target)
            else:
                if not os.path.isfile(f):
                    if os.path.isfile(os.path.realpath(f)):
                        f = os.path.realpath(f)
                    elif os.path.isfile(os.path.join(os.path.dirname(kic_path), f)):
                        f = os.path.join(os.path.dirname(kic_path), f)

                if not os.path.isfile(f):
                    raise Exception("ADD ERROR: %s NOT EXISTED" % f)
                shutil.copy(f,  target)

        return filenames

    def put_deps_to_build_path(self, deps, kic_build_folder):
        return []

    def build_kic(self, kic_path, kic_build_folder):
        commands = []
        author = self.configs.get("username", "anonymous")
        version = "1.0"
        website = ""
        summary = ""
        license = ""
        platform = "linux"

        name, ext = os.path.splitext(os.path.split(kic_path)[1])

        self.logger.debug("parsing %s" % kic_path)

        kic_content_list = self.get_kic_content(kic_path)

        for content in kic_content_list:
            if content and content[0] == "#":
                note_patterns = re.search(
                    '#\s*(AUTHOR|VERSION|WEBSITE|NAME|SUMMARY|LICENSE|PLATFORM)[:|\s]\s*(.+)',
                    content,
                    re.IGNORECASE
                )
                if note_patterns is not None:
                    group = note_patterns.groups()[0].lower()
                    if group == "author":
                        author = groups[1]
                    elif group == "version":
                        version = groups[1]
                    elif group == "website":
                        website = groups[1]
                    elif group == "name":
                        name = groups[1]
                    elif group == "summary":
                        summary = groups[1]
                    elif group == "license":
                        license = groups[1]
                    elif group == "platform":
                        platform = groups[1]

                continue

            patterns = re.search(self.re_pattern, content, re.IGNORECASE)
            if patterns is None:
                self.logger.response_error("build failed", "invalid content", content)
                return None

            key = patterns.groups()[0].lower()

            commands.append(self.handlers[key].parse(content))

        with open(os.path.join(kic_build_folder, "kics", "%s.kijc" % name), 'wb') as fs:
            simplejson.dump(commands, fs)

        self.logger.debug("parsed %s" % kic_path)

        if "t" in self.configs:
            tag = self.configs["t"]
            name, version = tag.split(":") if ":"in tag else (tag, version)
            author, name = name.split("/") if "/" in name else (author, name)

        return commands, author, version, website, name, summary, license, platform

    def get_kic_content(self, kic_path):
        contents = []
        with open(kic_path, "r") as fs:
            last_content = ""
            for content in fs:
                content = content.strip()
                if not content:
                    continue

                if content[-1] == "\\":
                    if not last_content:
                        last_content = content[:-1]
                    else:
                        last_content = "%s %s" % (last_content, content[:-1])
                    continue

                if last_content:
                    content = "%s %s" % (last_content, content)
                    last_content = ""
                contents.append(content)
        return contents

    def get_kic_info(self, option):
        if option[:7].lower() == "http://" or option[:8].lower() == "https://":
            urlinfo = urlparse.urlparse(option)
            filename = os.path.split(urlinfo["path"])[1]
            target = os.path.join(self.kindo_tmps_path, filename)

            download_with_progressbar(option, target)
            if os.path.isfile(target):
                return target, os.path.realpath(configs.get("o", self.startfolder))
            return None, None

        kic_maybe_paths = [
            option,
            os.path.join(self.startfolder, option),
            os.path.join(self.kindo_kics_path, option)
        ]

        for kic_maybe_path in kic_maybe_paths:
            if os.path.isfile(kic_maybe_path):
                kic_output_dir = self.configs.get("o", os.path.dirname(kic_maybe_path))
                if kic_output_dir[-3:].lower() == ".ki":
                    kic_output_dir = os.path.dirname(kic_output_dir)
                return kic_maybe_path, os.path.realpath(kic_output_dir)

        return None, None

    def zip_dir(self, dirname, zipfilename):
        filelist = []
        if os.path.isfile(dirname):
            filelist.append(dirname)
        else :
            for root, dirs, files in os.walk(dirname):
                for name in files:
                    filelist.append(os.path.join(root, name))

        zf = zipfile.ZipFile(zipfilename, "w", zipfile.ZIP_DEFLATED)
        if "kipwd" in self.configs and self.configs["kipwd"]:
            zf.setpassword(self.configs["kipwd"])

        for tar in filelist:
            arcname = tar[len(dirname):]
            zf.write(tar,arcname)

        zf.close()

