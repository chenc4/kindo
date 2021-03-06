#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import re
import time
import uuid
import codecs
import traceback
try:
    import urlparse
except:
    from urllib.parse import urlparse
import shutil
import zipfile
import json as simplejson

from kindo.kindo_core import KindoCore
from kindo.utils.functions import download_with_progressbar
from kindo.modules.run.add_command import AddCommand
from kindo.modules.run.check_command import CheckCommand
from kindo.modules.run.from_command import FromCommand
from kindo.modules.run.run_command import RunCommand
from kindo.modules.run.workdir_command import WorkdirCommand
from kindo.modules.run.download_command import DownloadCommand
from kindo.modules.run.ubuntu_command import UbuntuCommand
from kindo.modules.run.centos_command import CentOSCommand
from kindo.modules.run.addonrun_command import AddOnRunCommand
from kindo.modules.run.env_command import EnvCommand
from kindo.modules.run.maintainer_command import MaintainerCommand


class BuildModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

        self.kic_path_infos = []

        # get kics path from the command line
        # support to build multi kics with one command
        for option in options[2:]:
            filename, ext = os.path.splitext(option)
            if "." not in ext:
                ext = ".kic"
                option = "{0}.kic".format(option)

            if ext.lower() != ".kic":
                continue

            kic_path, outfolder = self.get_kic_info(option)
            if kic_path is not None and outfolder is None:
                self.logger.warn("invalid target: {0}".format(self.configs.get("o", "")))
                continue

            if kic_path is None or not kic_path:
                self.logger.warn("{0} not found".format(option))
                continue

            self.kic_path_infos.append(
                {
                    "path": kic_path,
                    "outfolder": outfolder
                }
            )

        # cache commands
        self.handlers = {
            "from": FromCommand(startfolder, configs, options, logger),
            "add": AddCommand(startfolder, configs, options, logger),
            "check": CheckCommand(startfolder, configs, options, logger),
            "run": RunCommand(startfolder, configs, options, logger),
            "workdir": WorkdirCommand(startfolder, configs, options, logger),
            "download": DownloadCommand(startfolder, configs, options, logger),
            "ubuntu": UbuntuCommand(startfolder, configs, options, logger),
            "centos": CentOSCommand(startfolder, configs, options, logger),
            "addonrun": AddOnRunCommand(startfolder, configs, options, logger),
            "env": EnvCommand(startfolder, configs, options, logger),
            "maintainer": MaintainerCommand(startfolder, configs, options, logger)
        }

        self.re_pattern = "^\s*(%s)\s+" % "|".join(self.handlers.keys())

    def start(self):
        try:
            if not self.kic_path_infos:
                self.logger.error("no kics")
                return

            for kic_path_info in self.kic_path_infos:
                if not os.path.isdir(kic_path_info["outfolder"]):
                    os.makedirs(kic_path_info["outfolder"])

                # build foder structure
                #   files
                #   images
                #   confs
                #       author-name-version.kic
                #       author-name-version.kijc
                #   manifest.json

                kic_build_folder = self.create_build_folder()

                output_ki_path = ""
                try:
                    commands, author, version, homepage, name, summary, license, platform = self.build_kic(
                        kic_path_info["path"], kic_build_folder
                    )

                    if commands is None:
                        return

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
                        os.path.join(kic_build_folder, "confs", "%s-%s-%s.kic" % (author, name, version))
                    )

                    files = []
                    images = []
                    for c in commands:
                        if "files" in c:
                            files += self.move_files_to_build_folder(
                                c["files"],
                                kic_build_folder,
                                kic_path_info["path"]
                            )

                        if "images" in c:
                            images += self.move_images_to_build_folder(
                                c["images"],
                                kic_build_folder
                            )

                    manifest_json = {
                        "name": name,
                        "version": version,
                        "author": author,
                        "homepage": homepage,
                        "summary": summary,
                        "license": license,
                        "platform": platform,
                        "build_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        "build_version": self.kindo_version,
                        "min_version": self.kindo_min_version,
                        "files": files,
                        "images": images
                    }

                    manifest = os.path.join(kic_build_folder, "manifest.json")
                    with open(manifest, 'wb') as fs:
                        fs.write(simplejson.dumps(manifest_json).encode("utf-8"))

                    output_ki_path = self.configs.get("o", kic_path_info["outfolder"])

                    if output_ki_path[-3:].lower() != ".ki":
                        output_ki_path = os.path.join(output_ki_path, "%s-%s-%s.ki" % (author, name, version))

                    output_ki_dir = os.path.dirname(output_ki_path)
                    if not os.path.isdir(output_ki_dir):
                        os.makedirs(output_ki_dir)

                    self.zip_dir(kic_build_folder, output_ki_path)
                except Exception as e:
                    self.logger.debug(traceback.format_exc())
                    self.logger.error(e)
                    return
                finally:
                    shutil.rmtree(kic_build_folder)
                self.logger.info("Successfully built {0} ==> {1}".format(kic_path_info["path"], output_ki_path))
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e)

    def create_build_folder(self):
        kic_build_folder = os.path.join(self.kindo_tmps_path, uuid.uuid4().hex)
        kic_build_sub_folders = [
            os.path.join(kic_build_folder, "confs"),
            os.path.join(kic_build_folder, "files"),
            os.path.join(kic_build_folder, "images")
        ]
        for kic_build_sub_folder in kic_build_sub_folders:
            if not os.path.isdir(kic_build_sub_folder):
                os.makedirs(kic_build_sub_folder)

        return kic_build_folder

    def move_files_to_build_folder(self, files, kic_build_folder, kic_path):
        file_names = []

        for f in files:
            if "name" not in f or "url" not in f:
                continue

            target = os.path.join(kic_build_folder, "files", f["name"])
            if f["url"][:7] == "http://" or f["url"][:8] == "https://":
                if not os.path.isfile(target):
                    download_with_progressbar(f["url"], target)
            elif not os.path.isfile(f["url"]):
                f["url"] = os.path.join(os.path.dirname(kic_path), f["url"])

                if not os.path.isfile(f["url"]):
                    raise Exception("{0} not found".format(f["url"]))

            if not os.path.isfile(target):
                shutil.copy(f["url"],  target)

            file_names.append(f["name"])
        return file_names

    def move_images_to_build_folder(self, images, kic_build_folder):
        image_names = []
        for image in images:
            if "name" not in image or "url" not in image:
                continue

            target = os.path.join(kic_build_folder, "images", image["name"])
            if not os.path.isfile(target):
                shutil.copy(image["url"],  target)

            if not os.path.isfile(target):
                raise Exception("failed to download {0}".format(image["name"]))

            image_names.append(image["name"])
        return image_names

    def build_kic(self, kic_path, kic_build_folder):
        commands, author, version, homepage, summary, license, platform = [], self.configs.get(
            "username",
            "anonymous"
        ), "latest", "", "", "", "linux"

        name, ext = os.path.splitext(os.path.split(kic_path)[1])

        kic_content_list = self.get_kic_content(kic_path)

        step = 0
        for kic_content in kic_content_list:
            content = kic_content["content"]
            if content[0] == "#":
                note_patterns = re.search(
                    '#\s*(AUTHOR|VERSION|HOMEPAGE|NAME|SUMMARY|LICENSE|PLATFORM)[:|\s]\s*(.+)',
                    content,
                    re.IGNORECASE
                )
                if note_patterns is not None:
                    groups = note_patterns.groups()
                    if len(groups) > 0:
                        group = groups[0].lower()

                        if group == "author":
                            author = groups[1]
                        elif group == "version":
                            version = groups[1]
                        elif group == "homepage":
                            homepage = groups[1]
                        elif group == "name":
                            name = groups[1]
                        elif group == "summary":
                            summary = groups[1]
                        elif group == "license":
                            license = groups[1]
                        elif group == "platform":
                            platform = groups[1]

                continue

            step += 1
            self.logger.info("Step %s : %s" % (step, content))

            patterns = re.search(self.re_pattern, content, re.IGNORECASE)
            if patterns is None:
                self.logger.error("    ---> line {0} invalid content".format(kic_content["line"]))
                return (None, None, None, None, None, None, None, None)

            key = patterns.groups()[0].lower()
            parsed_info = self.handlers[key].parse(content, kic_path)

            if not parsed_info or "args" not in parsed_info:
                self.logger.error("    ---> line {0} invalid content".format(kic_content["line"]))
                return (None, None, None, None, None, None, None, None)

            self.logger.info("    ---> %s" % (self._get_content_args_value(parsed_info["args"])))

            commands.append(parsed_info)

        with open(os.path.join(kic_build_folder, "confs", "{0}-{1}-{2}.kijc".format(author, name, version)), 'wb') as fs:
            fs.write(simplejson.dumps(commands).encode("utf-8"))

        if "t" in self.configs:
            tag = self.configs["t"]
            name, version = tag.split(":") if ":"in tag else (tag, version)
            author, name = name.split("/") if "/" in name else (author, name)

        return commands, author, version, homepage, name, summary, license, platform

    def get_kic_content(self, kic_path):
        contents = []

        line = 0
        with codecs.open(kic_path, "r", "utf-8") as fs:
            last_content = ""
            for content in fs:
                line += 1

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
                contents.append({"line": line, "content": content})
        return contents

    def get_kic_info(self, option):
        if option[:7].lower() == "http://" or option[:8].lower() == "https://":
            urlinfo = urlparse.urlparse(option)
            filename = os.path.split(urlinfo[1])[1]
            target = os.path.join(self.kindo_tmps_path, filename)

            download_with_progressbar(option, target)
            if os.path.isfile(target):
                return target, os.path.realpath(self.configs.get("o", self.startfolder))
            return None, None

        kic_maybe_paths = [
            option,
            os.path.join(self.startfolder, option),
            os.path.join(self.kindo_kics_path, option)
        ]

        for kic_maybe_path in kic_maybe_paths:
            if os.path.isfile(kic_maybe_path):
                kic_output_dir = self.configs.get("o", os.path.dirname(kic_maybe_path))
                if os.path.isfile(kic_output_dir):
                    if kic_output_dir[-3:].lower() != ".ki":
                        return kic_maybe_path, None

                if kic_output_dir[-3:].lower() == ".ki":
                    kic_output_dir = os.path.dirname(kic_output_dir)
                return kic_maybe_path, os.path.realpath(kic_output_dir)

        return None, None

    def zip_dir(self, dirname, zipfilename):
        filelist = []
        if os.path.isfile(dirname):
            filelist.append(dirname)
        else:
            for root, dirs, files in os.walk(dirname):
                for name in files:
                    filelist.append(os.path.join(root, name))

        zf = zipfile.ZipFile(zipfilename, "w", zipfile.ZIP_DEFLATED)
        if "kipwd" in self.configs and self.configs["kipwd"]:
            zf.setpassword(self.configs["kipwd"])

        for tar in filelist:
            arcname = tar[len(dirname):]
            zf.write(tar, arcname)

        zf.close()

    def _get_content_args_value(self, args):
        args_strings = []

        if isinstance(args, dict):
            for k, v in args.items():
                args_strings.append("%s : %s " % (k, v))
        elif isinstance(args, list):
            for arg in args:
                if isinstance(arg, dict):
                    for k, v in arg.items():
                        args_strings.append("%s : %s " % (k, v))

        return "; ".join(args_strings)
