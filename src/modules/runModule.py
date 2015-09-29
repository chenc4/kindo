#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import shutil
import traceback
import zipfile
import pickle
import requests
import simplejson
from fabric.state import output
from fabric.tasks import execute
from fabric.api import env
from core.kindoCore import KindoCore
from utils.configParser import ConfigParser
from utils.kindoUtils import download_with_progressbar
from commands.addCommand import AddCommand
from commands.checkCommand import CheckCommand
from commands.runCommand import RunCommand
from commands.workdirCommand import WorkdirCommand
from commands.downloadCommand import DownloadCommand
from commands.ubuntuCommand import UbuntuCommand
from commands.centosCommand import CentOSCommand
from commands.addOnRunCommand import AddOnRunCommand
from commands.envCommand import EnvCommand


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
            if not os.path.isfile(self.configs["ssh"]):
                logger.warn("ssh config not found: %s" % self.configs["ssh"])
            else:
                env.use_ssh_config = True
                env.ssh_config_path = self.configs["ssh"]

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
        if not os.path.isfile(self.ki_path):
            self.logger.response("ki not found: %s" % self.ki_path, False)
            return

        if env.passwords is None or len(env.passwords) == 0:
            self.logger.response("hosts not found", False)
            return

        dirname, filename = os.path.split(self.ki_path)
        cache_folder, length = self.get_cache_info(filename)
        if (
            length != os.path.getsize(self.ki_path) or
            not os.path.isdir(cache_folder)
        ):
            if not self.unzip_file(self.ki_path, cache_folder):
                self.logger.response("unpackage failed", False)
                return

        ki_kibcs_path = os.path.join(cache_folder, "kibcs")
        ki_files_path = os.path.join(cache_folder, "files")

        # 兼容老版本的安装包
        if not os.path.isdir(ki_kibcs_path):
            ki_kibcs_path = os.path.join(cache_folder, "confs")

        if not os.path.isdir(ki_files_path):
            ki_files_path = os.path.join(cache_folder, "deps")

        if not os.path.isdir(ki_kibcs_path):
            self.logger.response("invalid ki package", False)
            return

        try:
            for f in os.listdir(ki_kibcs_path):
                filename, ext = os.path.splitext(f)
                if ext != ".kibc":
                    continue

                script = os.path.join(ki_kibcs_path, f)
                with open(script, 'rb') as fs:
                    script_commands = pickle.load(fs)

                    execute(
                        self.execute_script_commands,
                        commands=script_commands,
                        depsdir=ki_files_path,
                        hosts=env.passwords.keys()
                    )
            self.logger.response("run ok")
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.response(e, False)

    def execute_script_commands(self, commands, depsdir):
        position = "~"
        envs = self.configs if self.configs is not None else {}

        for command in commands:
            if "action" not in command:
                raise Exception("command invalid")

            action = command["action"].lower()
            if action not in self.handlers:
                raise Exception("%s not supported" % action)

            status, position, errormsg, _envs = self.handlers[action].run(
                command=command,
                depsdir=depsdir,
                position=position,
                envs=envs
            )
            envs = dict(_envs, **envs)
            # if the command is executed(success or fail), not continue
            if status == 0:
                self.logger.debug(errormsg)

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
        cf.set(image_info["name"], "pusher", image_info["pusher"])
        cf.set(image_info["name"], "size", image_info["size"])
        cf.set(image_info["name"], "url", image_info["url"])
        cf.set(image_info["name"], "path", path)

        cf.write(open(ini_path, "w"))
        return True

    def get_cache_info(self, filename):
        # for example: /var/cache/kindo/nginx/nginx-1.0.0
        whole_name, ext = os.path.splitext(filename)
        last_hyphen_pos = whole_name.rfind("-")
        name = whole_name if last_hyphen_pos == -1 else whole_name[:last_hyphen_pos]

        cache_folder = os.path.join(self.kindo_caches_path, name, whole_name)
        cache_file = os.path.join(cache_folder, "ki.cache")
        if not os.path.isfile(cache_file):
            return cache_folder, 0

        with open(cache_file, "r") as fs:
            try:
                return cache_folder, int(fs.read())
            except:
                return cache_folder, 0

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


