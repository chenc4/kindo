#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import shutil
import tempfile
import zipfile
import pickle
from fabric.state import output
from fabric.tasks import execute
from fabric.api import env
from commands.add import Add
from commands.check import Check
from commands.run import Run
from commands.workdir import Workdir
from commands.download import Download


class KiParse:
    def __init__(self, ki_path, options, logger):
        self.ki_path = ki_path
        self.options = options
        self.logger = logger

        self.host = options.get("h", None)
        self.password = options.get("p", None)

        if self.host is None or self.password is None:
            return

        self.host = "%s:22" % self.host if self.host.rfind(":") == -1 else self.host
        self.host = "root@%s" % self.host if self.host.rfind("@") == -1 else self.host

        self.handlers = [Add(), Check(), Run(), Workdir(), Download()]

        env.colorize_errors = True
        env.command_timeout = 60 * 30
        env.passwords = {self.host: self.password}
        env.output_prefix = ""
        output.debug = False
        output.running = False

    def start(self):
        if self.host is None or self.password is None:
            self.logger.error("please input -h and -p")
            return

        try:
            if not os.path.isfile(self.ki_path):
                self.logger.error("the ki file not found")
                return

            tempfolder = tempfile.mkdtemp()

            try:
                if not self.unzip_file(self.ki_path, tempfolder):
                    logger.error("execute failed")
                    return

                conffolder = os.path.join(tempfolder, "conf")
                depsfolder = os.path.join(tempfolder, "deps")

                for f in os.listdir(conffolder):
                    filename, ext = os.path.splitext(f)
                    if ext != ".kibc":
                        continue

                    config = os.path.join(conffolder, f)
                    with open(config, 'rb') as fs:
                        commands = pickle.load(fs)

                        try:
                            execute(self.executes, commands=commands, deps_folder=depsfolder, hosts=[self.host])
                        except:
                            shutil.rmtree(tempfolder)
                            self.logger.error("""
<--------------------------------KINDO-------------------------------->
                                FAILED
<--------------------------------------------------------------------->""")
                            return
                self.logger.info("""
<--------------------------------KINDO-------------------------------->
                                SUCCESS
<--------------------------------------------------------------------->""")
            except:
                self.logger.error("execute failed")

            shutil.rmtree(tempfolder)
        except:
            self.logger.error("execute failed")

    def executes(self, commands, deps_folder):
        position = "~"
        for command in commands:
            for handler in self.handlers:
                isok = handler.run(command, deps_folder, position)
                if isok:
                    position = handler.get_posiotion()
                    break

    def unzip_file(self, zipfilename, unziptodir):
        try:
            if not os.path.exists(unziptodir):
                os.mkdir(unziptodir)

            zfobj = zipfile.ZipFile(zipfilename)
            for name in zfobj.namelist():
                name = name.replace('\\','/')

                if name.endswith('/'):
                    os.mkdir(os.path.join(unziptodir, name))
                else:
                    ext_filename = os.path.join(unziptodir, name)
                    ext_dir= os.path.dirname(ext_filename)
                    if not os.path.exists(ext_dir):
                        os.mkdir(ext_dir)

                    with open(ext_filename, 'wb') as fs:
                        fs.write(zfobj.read(name))

            return True
        except:
            self.logger.warn("failed to unpackage .ki ")
        return False
