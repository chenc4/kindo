#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import shutil
import traceback
import zipfile
import pickle
import requests
import hashlib
import simplejson

from fabric.api import env, output, execute

from kindo.kindo_core import KindoCore
from kindo.utils.config_parser import ConfigParser
from kindo.utils.functions import download_with_progressbar
from kindo.commands.add_command import AddCommand
from kindo.commands.check_command import CheckCommand
from kindo.commands.run_command import RunCommand
from kindo.commands.workdir_command import WorkdirCommand
from kindo.commands.download_command import DownloadCommand
from kindo.commands.ubuntu_command import UbuntuCommand
from kindo.commands.centos_command import CentOSCommand
from kindo.commands.addOnRun_command import AddOnRunCommand
from kindo.commands.env_command import EnvCommand


class RunModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

        env.colorize_errors = True
        env.command_timeout = self.configs.get("timout", 60 * 30)
        env.output_prefix = ""
        env.passwords = {}
        output.debug = False
        output.running = False

        host = configs.get("h", None)
        host = "%s:22" % host if host is not None and host.rfind(":") == -1 else host
        host = "root@%s" % host if host is not None and host.rfind("@") == -1 else host

        password = configs.get("p", "")

        if host is not None:
            env.passwords[host] = password

        hosts = self.get_hosts_setting()

        groups = configs["g"].split(",") if "g" in configs else []
        for group in groups:
            group = group.strip()

            if group not in hosts:
                self.logger.warn("GROUP NOT FOUND: %s" % group)
                continue

            for k, v in hosts[group].items():
                env.passwords[k] = v

        if len(env.passwords) == 0 and "default" in hosts:
            for k, v in hosts["default"].items():
                env.passwords[k] = v

        if "ssh" in self.configs:
            env.use_ssh_config = True
            env.ssh_config_path = os.path.realpath(self.configs["ssh"])

        self.ki_path = self.get_ki_path()

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

    def start(self):
        if env.passwords is None or len(env.passwords) == 0:
            self.logger.error("hosts not found")
            return

        self.run_ki(self.ki_path)

    def run_ki(self, ki_path):
        if not os.path.isfile(ki_path):
            self.logger.error("{0} not found".format(ki_path))
            return

        ki_unpackage_folder = self.get_ki_unpackage_folder()

        ki_confs_path = os.path.join(ki_unpackage_folder, "confs")
        ki_files_path = os.path.join(ki_unpackage_folder, "files")
        ki_images_path = os.path.join(ki_unpackage_folder, "images")
        ki_manifest_path = os.path.join(ki_unpackage_folder, "manifest.json")

        # downward compatible
        if not os.path.isdir(ki_confs_path):
            ki_confs_path = os.path.join(ki_unpackage_folder, "kibcs")

        if not os.path.isdir(ki_files_path):
            ki_files_path = os.path.join(ki_unpackage_folder, "deps")

        if not os.path.isdir(ki_confs_path) or not os.path.isfile(ki_manifest_path):
            self.logger.error("invalid ki package")
            return

        manifest = {}
        try:
            with open(ki_manifest_path, "wb") as fs:
                manifest = simplejson.loads(fs)
                self.test_whether_compatible(manifest)

                if "images" in manifest:
                    for image_name in manifest["images"]:
                        image_path = os.path.join(ki_images_path, image_name)

                        self.run_ki(image_path)

            for f in os.listdir(ki_confs_path):
                filename, ext = os.path.splitext(f)
                if ext not in [".kibc", ".kijc"]:
                    continue

                script = os.path.join(ki_confs_path, f)
                with open(script, 'rb') as fs:
                    # 兼容早期配置文件
                    if ext == ".kibc":
                        script_commands = pickle.load(fs)
                    elif ext == ".kijc":
                        script_commands = simplejson.loads(fs)

                    execute(
                        self.execute_script_commands,
                        commands=script_commands,
                        filesdir=ki_files_path,
                        imagesdir=ki_images_path,
                        hosts=env.passwords.keys()
                    )
            self.logger.info("run ok")
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e)
        finally:
            try:
                rm_file_commands = []
                if "files" in manifest:
                    for f in manifest["files"]:
                        rm_file_commands.append(
                            {
                                "action": "RUN",
                                "args": {"command": "rm -f \"{0}\"".format(f)},
                                "variables": []
                            }
                        )
                execute(
                    self.execute_script_commands,
                    commands=rm_file_commands,
                    filesdir=[],
                    imagesdir=[],
                    hosts=env.passwords.keys()
                )
            except:
                self.logger.debug(traceback.format_exc())

    def execute_script_commands(self, commands, filesdir, imagesdir):
        position = "~"
        envs = self.configs if self.configs is not None else {}

        for command in commands:
            if "action" not in command:
                raise Exception("command invalid")

            action = command["action"].lower()
            if action not in self.handlers:
                raise Exception("{0} not supported".format(action))

            position, _envs = self.handlers[action].run(
                command=command,
                filesdir=filesdir,
                imagesdir=imagesdir,
                position=position,
                envs=envs
            )
            envs = dict(_envs, **envs)

    def test_whether_compatible(self, manifest):
        if "min_version" in manifest and manifest["min_version"] > self.kindo_version:
            raise Exception("the min version is too high")

        if "name" not in manifest or "author" not in manifest or "version" not in manifest:
            raise Exception("invalid manifest")


    def get_ki_path(self):
        self.logger.debug(self.options)

        ki_path = ""
        for option in self.options[2:]:
            ki_path = option
            if ki_path[-3:] != ".ki":
                ki_path = "%s.ki" % ki_path


            if not os.path.isfile(ki_path):
               path = os.path.realpath(ki_path)
               if not os.path.isfile(path):
                    path = os.path.join(self.startfolder, ki_path)
                    if not os.path.isfile(path):
                        path = self.get_image_path(option)
                        self.logger.debug("get_image_path: %s" % path)
                        self.logger.debug("option: %s" % option)
                        if not path and "/" in option and ":" in option:
                            path = self.pull_image_path(option)


                    if os.path.isfile(path):
                        ki_path = path

            if os.path.isfile(ki_path):
                break

        self.logger.debug(ki_path)
        return ki_path

    def pull_image_path(self, imagename):
        pull_engine_url = self.get_pull_engine_url()
        try:
            response = self.pull_image_info(pull_engine_url, imagename)
            if response is None:
                self.logger.debug(response)
                return

            if "code" in response:
                if response["code"] == "040014000":
                    code = prompt("please input the extraction code: ")
                    response = self.pull_image_info(pull_engine_url, imagename, {"code": code})

                if "code" in response:
                    raise Exception(response["msg"])

            path = self.download_package(response)
            if not self.add_image_info(response, path):
                raise Exception("pull failed")
            return path
        except:
            self.logger.debug(traceback.format_exc())
        return ""

    def get_pull_engine_url(self):
        pull_engine_url = "%s/v1/pull" % self.configs.get("index", "kindo.cycore.cn")

        if pull_engine_url[:7].lower() != "http://" and pull_engine_url[:8].lower() != "https://":
            pull_engine_url = "http://%s" % pull_engine_url

        return pull_engine_url

    def pull_image_info(self, pull_engine_url, imagename, params=None):
        name, version = imagename.split(":") if ":"in imagename else (imagename, "")
        author, name = name.split("/") if "/" in name else ("", name)

        params = dict({"uniqueName": name}, **params) if params is not None else {"uniqueName": name}
        if author:
            params["uniqueName"] = "%s/%s" % (author, params["uniqueName"])
        else:
            params["uniqueName"] = "anonymous/%s" % params["uniqueName"]

        if version:
            params["uniqueName"] = "%s:%s" % (params["uniqueName"], version)
        else:
            params["uniqueName"] = "%s:1.0" % params["uniqueName"]

        r = requests.get(pull_engine_url, params=params)
        if r.status_code != 200:
            raise Exception("\"%s\" can't connect" % pull_engine_url)

        return r.json()

    def download_package(self, image_info):
        url = image_info["url"]
        name = image_info["name"]

        self.logger.debug("downloading %s from %s" % (name, url))

        kiname = name.replace("/", "-").replace(":", "-")
        kiname = kiname if name[-3:] == ".ki" else "%s.ki" % kiname
        target = os.path.join(self.kindo_images_path, kiname)

        try:
            if os.path.isfile(target):
                self.logger.debug("%s existed, removing" % target)
                os.remove(target)

            if not os.path.isdir(self.kindo_images_path):
                os.makedirs(self.kindo_images_path)

            download_with_progressbar(url, target)

            return target
        except:
            self.logger.debug(traceback.format_exc())
        return ""

    def add_image_info(self, image_info, path):
        if not path:
            self.logger.debug("path is empty")
            return False

        ini_path = os.path.join(self.kindo_settings_path, "images.ini")
        if not os.path.isdir(self.kindo_settings_path):
            os.makedirs(self.kindo_settings_path)

        cf = ConfigParser()
        cf.read(ini_path)

        sections = cf.sections()

        if image_info["name"] not in sections:
            cf.add_section(image_info["name"])
        cf.set(image_info["name"], "name", image_info["name"])
        cf.set(image_info["name"], "version", image_info["version"])
        cf.set(image_info["name"], "buildtime", image_info["buildtime"])
        cf.set(image_info["name"], "maintainer", image_info["maintainer"])
        cf.set(image_info["name"], "size", image_info["size"])
        cf.set(image_info["name"], "url", image_info["url"])
        cf.set(image_info["name"], "path", path)

        cf.write(open(ini_path, "w"))
        return True

    def get_ki_unpackage_folder(self, ki_path):
        ki_path_md5 = hashlib.md5().update(self.ki_path).hexdigest()

        ki_unpackage_folder = os.path.join(self.kindo_caches_path, ki_path_md5)
        ki_length_cache_file = os.path.join(ki_unpackage_folder, "ki.cache")

        length = -1
        if os.path.isfile(ki_length_cache_file):
            with open(ki_length_cache_file, "r") as fs:
                length = int(fs.read())

        if not os.path.isdir(ki_unpackage_folder):
            os.makedirs(ki_unpackage_folder)

        ki_length = os.path.getsize(ki_path)
        if length != ki_length:
            if not self.unzip_file(ki_path, ki_unpackage_folder):
                raise Exception("unpackage failed")

            with open(ki_length_cache_file, "wb") as fs:
                fs.write(ki_length)
        return ki_unpackage_folder

    def get_image_path(self, section):
        ini_path = os.path.join(self.kindo_settings_path, "images.ini")
        if not os.path.isfile(ini_path):
            return ""

        cf = ConfigParser()
        cf.read(ini_path)

        sections = cf.sections()

        if section in sections:
            items = cf.items(section)

            for k, v in items:
                if k == "path":
                    return v
        return ""

    def unzip_file(self, zipfilename, unziptodir):
        try:
            if not os.path.exists(unziptodir):
                os.makedirs(unziptodir)

            zfobj = zipfile.ZipFile(zipfilename)

            if "kipwd" in self.configs and self.configs["kipwd"]:
                zfobj.setpassword(self.configs["kipwd"])

            for name in zfobj.namelist():
                name = name.replace('\\','/')

                if name.endswith('/'):
                    os.makedirs(os.path.join(unziptodir, name))
                else:
                    ext_filename = os.path.join(unziptodir, name)
                    ext_dir= os.path.dirname(ext_filename)
                    if not os.path.exists(ext_dir):
                        os.makedirs(ext_dir)

                    with open(ext_filename, 'wb') as fs:
                        fs.write(zfobj.read(name))

            return True
        except Exception as e:
            self.logger.debug(traceback.format_exc())
        return False

    def get_hosts_setting(self):
        ini_path = os.path.join(self.kindo_settings_path, "hosts.ini")
        if not os.path.isfile(ini_path):
            return {}

        cf = ConfigParser()
        cf.read(ini_path)

        hosts = {}
        for section in cf.sections():
            items = cf.items(section)
            section = section.lower()

            hosts[section] = {}
            for host, password in items:
                host = host.strip()
                password = password.strip()

                host = "%s:22" % host if host is not None and host.rfind(":") == -1 else host
                host = "root@%s" % host if host is not None and host.rfind("@") == -1 else host

                hosts[section][host] = password
        return hosts


