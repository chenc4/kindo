#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import re
import time
import uuid
import tempfile
import traceback
import requests
import shutil
import pickle
import zipfile
import simplejson
from modules.kindoModule import KindoModule
from commands.addCommand import AddCommand
from commands.checkCommand import CheckCommand
from commands.runCommand import RunCommand
from commands.workdirCommand import WorkdirCommand
from commands.downloadCommand import DownloadCommand
from commands.ubuntuCommand import UbuntuCommand
from commands.centosCommand import CentOSCommand


class BuildModule(KindoModule):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoModule.__init__(self, command, startfolder, configs, options, logger)

        self.kic_path_infos = []
        for option in options:
            filename, ext = os.path.splitext(option)
            if "." not in ext:
                ext = ".kic"
                option = "%s.kic" % option

            if ext.lower() != ".kic":
                continue

            kic_path, outfolder = self.get_kic_info(option)
            if kic_path is None or not kic_path:
                self.logger.debug("KIC NOT FOUND")
                continue

            self.kic_path_infos.append(
                {
                    "path": kic_path,
                    "outfolder": outfolder
                }
            )

        self.handlers = {
            "add": AddCommand(),
            "check": CheckCommand(),
            "run": RunCommand(),
            "workdir": WorkdirCommand(),
            "download": DownloadCommand(),
            "ubuntu": UbuntuCommand(),
            "centos": CentOSCommand()
        }

        self.re_pattern =  "^\s*(%s)\s+" % "|".join(self.handlers.keys())

    def start(self):
        kic_build_number = 0
        for kic_path_info in self.kic_path_infos:
            kic_build_number += 1

            if not os.path.isdir(kic_path_info["outfolder"]):
                try:
                    os.makedirs(kic_path_info["outfolder"])
                except:
                    self.logger.debug(traceback.format_exc())
                    self.logger.error("OUTFOLDER CREATE FAILED: %s" % kic_path_info["outfolder"])
                    return

            kic_build_folder = os.path.join(self.kindo_tmps_path, uuid.uuid4().hex)
            if not os.path.isdir(kic_build_folder):
                try:
                    kic_build_sub_folders = [
                        os.path.join(kic_build_folder, "kics"),
                        os.path.join(kic_build_folder, "kibcs"),
                        os.path.join(kic_build_folder, "files")
                    ]
                    for kic_build_sub_folder in kic_build_sub_folders:
                        os.makedirs(kic_build_sub_folder)
                except:
                    self.logger.debug(traceback.format_exc())
                    self.logger.error("TMPFOLDER CREATE FAILED: %s" % kic_build_folder)
                    return

            try:
                filedir, filename = os.path.split(kic_path_info["path"])

                commands, author, version, website, name, summary, license = self.build_kic(
                    kic_path_info["path"], kic_build_folder
                )
                if commands is None:
                    return

                if len(re.findall("[^a-zA-Z0-9]", author)) > 0:
                    self.logger.error("INVALID AUTHOR NAME, JUST ALLOW 'a-zA-Z0-9-_'")
                    return

                if len(re.findall("[^a-zA-Z0-9-_]", name)) > 0:
                    self.logger.error("INVALID NAME, JUST ALLOW 'a-zA-Z0-9-_'")
                    return

                if len(re.findall("[^a-zA-Z0-9\.-]", version)) > 0:
                    self.logger.error("INVALID VERSION, JUST ALLOW 'a-zA-Z0-9\.-'")
                    return

                shutil.copy(kic_path_info["path"],  os.path.join(kic_build_folder, "kics", filename))

                files = []
                for c in commands:
                    if "files" in c:
                        files += self.put_files_to_build_path(
                            c["files"],
                            kic_build_folder,
                            kic_path_info["path"]
                        )

                manifest_json = {
                    "name": name,
                    "version": version,
                    "author": author,
                    "website": website,
                    "summary": summary,
                    "license": license,
                    "buildtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    "buildversion": 2,
                    "filename": filename,
                    "files": files
                }

                if len(self.kic_path_infos) == 1:
                    manifest = os.path.join(kic_build_folder, "manifest.json")
                else:
                    manifest = os.path.join(kic_build_folder, "manifest-%s.json" % kic_build_number)
                with open(manifest, 'wb') as fs:
                    simplejson.dump(manifest_json, fs)

                output_ki_path = os.path.join(kic_path_info["outfolder"], "%s.ki" % name)

                self.logger.info("packaging %s" % output_ki_path)
                self.zip_dir(kic_build_folder, output_ki_path)
                self.logger.info("packaged %s" % output_ki_path)
            except:
                self.logger.debug(traceback.format_exc())
                self.logger.error("BUILD FAILED: exception raised")
            finally:
                shutil.rmtree(kic_build_folder)


    def put_files_to_build_path(self, files, kic_build_folder, kic_path):
        filenames = []
        for f in files:
            filename = re.sub("[\?|\+|\*|\<|\>|:]", "", os.path.split(f)[1])
            filenames.append(filename)

            target = os.path.join(kic_build_folder, "files", filename)
            if f[:7].lower() == "http://" or f[:8].lower() == "https://":
                r = requests.get(f)
                if r.status_code == 200:
                    with open(target, "wb") as fs:
                        fs.write(r.content)
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


    def build_kic(self, kic_path, kic_build_folder):
        commands = []
        deps = []
        author = self.configs.get("username", "anonymous")
        version = "1.0"
        website = ""
        summary = ""
        license = ""

        filedir, filename = os.path.split(kic_path)
        name, ext = os.path.splitext(filename)

        self.logger.info("parsing %s" % kic_path)
        with open(kic_path, "r") as fs:
            line = 0
            for content in fs:
                line += 1

                content = content.strip()
                if content and content[0] == "#":
                    patterns = re.search(
                        '#\s*(AUTHOR|VERSION|WEBSITE|NAME|SUMMARY|LICENSE)[:|\s]\s*(.+)',
                        content,
                        re.IGNORECASE
                    )
                    if patterns is not None:
                        groups = patterns.groups()
                        if groups[0].lower() == "author":
                            author = groups[1]
                            self.logger.info("parsed author: %s" % author)
                        elif groups[0].lower() == "version":
                            version = groups[1]
                            self.logger.info("parsed version: %s" % version)
                        elif groups[0].lower() == "website":
                            website = groups[1]
                            self.logger.info("parsed website: %s" % website)
                        elif groups[0].lower() == "name":
                            name = groups[1]
                            self.logger.info("parsed name: %s" % name)
                        elif groups[0].lower() == "summary":
                            summary = groups[1]
                        elif groups[0].lower() == "license":
                            license = groups[1]
                            self.logger.info("parsed license: %s" % license)
                    continue

                if not content:
                    continue

                patterns = re.search(self.re_pattern, content, re.IGNORECASE)
                if patterns is None:
                    self.logger.error("BUILD FAILED (LINE: %s): invalid content" % line)
                    return None, None, None, None, None, None, None

                key = patterns.groups()[0].lower()

                command = self.handlers[key].parse(content)
                if command:
                    command["line"] = line
                    command["content"] = content
                    commands.append(command)

        with open(os.path.join(kic_build_folder, "kibcs", "%s.kibc" % name), 'wb') as fs:
            pickle.dump(commands, fs)
        self.logger.info("parsed %s" % kic_path)

        if "t" in self.configs:
            tag = self.configs["t"]
            name, version = tag.split(":") if ":"in tag else (tag, version)
            author, name = name.split("/") if "/" in name else (author, name)

        return commands, author, version, website, name, summary, license

    def get_kic_info(self, option):
        if option[:7].lower() == "http://" or option[:8].lower() == "https://":
            filename = re.sub("[\?|\+|\*|\<|\>|:| ]", "", os.path.split(option)[1])
            target = os.path.join(self.kindo_tmps_path, filename)
            r = requests.get(option)
            if r.status_code == 200:
                with open(target, "wb") as fs:
                    fs.write(r.content)

                return target, os.path.realpath(configs.get("o", self.startfolder))

        kic_maybe_paths = [
            option,
            os.path.join(self.startfolder, "kics", option),
            os.path.join(self.startfolder, option),
            os.path.join(self.kindo_kics_path, option)
        ]

        for kic_maybe_path in kic_maybe_paths:
            if os.path.isfile(kic_maybe_path):
                return kic_maybe_path, os.path.realpath(self.configs.get("o", os.path.dirname(kic_maybe_path)))

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

