#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import re
import uuid
import tempfile
import requests
import shutil
import pickle
import zipfile
from commands.add import Add
from commands.check import Check
from commands.run import Run
from commands.workdir import Workdir
from commands.download import Download

class KicParse:
    def __init__(self, kic_path, options, logger):
        self.kic_path = kic_path
        self.outfolder = os.path.realpath(options.get("o", os.path.dirname(self.kic_path)))
        self.logger = logger

        self.handlers = [Add(), Check(), Run(), Workdir(), Download()]

    def start(self):
        if not os.path.isfile(self.kic_path):
            logger.warn("%s not existed" % self.kic_path)
            return

        if not os.path.isdir(self.outfolder):
            os.makedirs(self.outfolder)

        try:
            commands = []

            deps = []
            fs = open(self.kic_path, "r")
            for line in fs:
                line = line.strip()
                if line and line[0] == "#":
                    continue

                for handler in self.handlers:
                    command = handler.parse(line)
                    if command:
                        commands.append(command)

                        deps += handler.get_deps()
                        break

            tempfolder = tempfile.mkdtemp()
            for folder in [os.path.join(tempfolder, "deps"), os.path.join(tempfolder, "conf")]:
                if not os.path.isdir(folder):
                    os.makedirs(folder)

            with open(os.path.join(tempfolder, "conf", "%s.kibc" % uuid.uuid4().hex), 'wb') as fs:
                pickle.dump(commands, fs)

            for dep in deps:
                filename = re.split("[\?|\+|\*|\<|\>|:]", os.path.split(dep)[1])
                target = os.path.join(tempfolder, "deps", filename[0])
                if dep[:7].lower() == "http://" or dep[:8].lower() == "https://":
                    r = requests.get(dep)
                    if r.status_code == 200:
                        with open(target, "wb") as fs:
                            fs.write(r.content)
                else:
                    shutil.copy(dep,  target)

            zipfile = os.path.join(self.outfolder, "%s.ki" % os.path.split(os.path.splitext(self.kic_path)[0])[1])
            if self.zip_dir(tempfolder, zipfile):
                self.logger.info("compile ok")
            else:
                self.logger.error("compile failed")

            shutil.rmtree(tempfolder)
        except:
            self.logger.error("compile failed")

    def zip_dir(self, dirname, zipfilename):
        try:
            filelist = []
            if os.path.isfile(dirname):
                filelist.append(dirname)
            else :
                for root, dirs, files in os.walk(dirname):
                    for name in files:
                        filelist.append(os.path.join(root, name))

            zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
            for tar in filelist:
                arcname = tar[len(dirname):]
                zf.write(tar,arcname)
            zf.close()

            return True
        except:
            self.logger.error("failed to package .kic to .ki")
        return False

