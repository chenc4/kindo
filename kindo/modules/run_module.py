#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import traceback
import zipfile
import pickle
import simplejson
from multiprocessing import Pool

from kindo.kindo_core import KindoCore
from kindo.utils.kissh import KiSSHClient
from kindo.utils.config_parser import ConfigParser
from kindo.utils.functions import download_with_progressbar, get_md5
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


class RunModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

        host = self.configs.get("h", self.configs.get("host", ""))
        password = self.configs.get("p", self.configs.get("password", ""))
        groups = self.configs.get("g", self.configs.get("group", []))

        host = "%s:22" % host if host is not None and host.rfind(":") == -1 else host
        host = "root@%s" % host if host is not None and host.rfind("@") == -1 else host

        self.activate_hosts = []

        hosts = self.get_hosts_setting()
        for group in groups:
            group = group.strip()

            if group not in hosts:
                self.logger.warn("GROUP NOT FOUND: %s" % group)
                continue

            for k, v in hosts[group].items():
                self.activate_hosts.append({k: v})

        if host:
            self.activate_hosts.append({host: password})

        self.ki_paths = self.get_ki_paths()

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

    def start(self):
        if len(self.activate_hosts) == 0:
            self.logger.error("hosts not found")
            return

        run_infos = []
        for ki_path in self.ki_paths:
            image_run_infos = self.get_image_run_infos(ki_path)

            for host_info in self.activate_hosts:
                run_infos.append({"host_info": host_info, "image_run_infos": image_run_infos})

        print(run_infos)
        # 多进程执行命令
        processes = 10 if len(self.ki_paths) > 10 else len(self.ki_paths)
        pool = Pool(processes=processes)
        pool.apply_async(self.execute, run_infos)
        pool.close()
        pool.join()

    def get_image_run_infos(self, ki_path):
        image_run_infos = []

        try:
            ki_unpackage_folder = self.get_ki_unpackage_folder(ki_path)

            ki_confs_path, ki_files_path, ki_images_path, ki_manifest_path = self.get_image_standard_folders(
                ki_unpackage_folder)

            if not os.path.isdir(ki_confs_path) or not os.path.isfile(ki_manifest_path):
                self.logger.error("invalid image")
                return

            manifest = {}

            with open(ki_manifest_path, "rb") as fs:
                manifest = simplejson.load(fs)
                if not self.is_compatible_and_valid_image(manifest):
                    self.logger.error("invalid image")
                    return

                if "images" in manifest:
                    for image_name in manifest["images"]:
                        image_path = os.path.join(ki_images_path, image_name)
                        image_run_infos.extend(self.get_image_run_infos(image_path))

            for f in os.listdir(ki_confs_path):
                filename, ext = os.path.splitext(f)
                if ext not in [".kibc", ".kijc"]:
                    continue

                script = os.path.join(ki_confs_path, f)
                with open(script, 'rb') as fs:
                    script_commands = []
                    #  backward-compatible
                    if ext == ".kibc":
                        script_commands = pickle.load(fs)
                    elif ext == ".kijc":
                        script_commands = simplejson.load(fs)

                    if not script_commands:
                        self.logger.warn("empty commands: {0}".format(script))
                        continue

                    image_run_infos.append(
                        {
                            "commands": script_commands,
                            "ki_files_path": ki_files_path,
                            "ki_images_path": ki_images_path,
                            "ki_path": ki_path,
                            "files": manifest.get("files", [])
                        }
                    )
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e)

        return image_run_infos

    def get_image_standard_folders(self, ki_unpackage_folder):
        ki_confs_path = os.path.join(ki_unpackage_folder, "confs")
        ki_files_path = os.path.join(ki_unpackage_folder, "files")
        ki_images_path = os.path.join(ki_unpackage_folder, "images")
        ki_manifest_path = os.path.join(ki_unpackage_folder, "manifest.json")
        # downward compatible
        if not os.path.isdir(ki_confs_path):
            ki_confs_path = os.path.join(ki_unpackage_folder, "kibcs")
        if not os.path.isdir(ki_files_path):
            ki_files_path = os.path.join(ki_unpackage_folder, "deps")
        return ki_confs_path, ki_files_path, ki_images_path, ki_manifest_path

    def execute(self, run_info):
        try:
            position = "~"
            envs = self.configs if self.configs is not None else {}

            with KiSSHClient(run_info["host_info"]) as ssh_client:
                image_run_infos = run_info["image_run_infos"]
                ki_files_path = run_info["ki_files_path"]
                ki_images_path = run_info["ki_images_path"]
                ki_path = run_info["ki_path"]
                files = run_info["files"]

                try:
                    for image_run_info in image_run_infos:
                        commands = image_run_info["commands"]

                        for command in commands:
                            if "action" not in command:
                                raise Exception("command invalid")

                            action = command["action"].lower()
                            if action not in self.handlers:
                                raise Exception("{0} not supported".format(action))

                            position, _envs = self.handlers[action].run(
                                ssh_client,
                                command,
                                ki_files_path,
                                ki_images_path,
                                position,
                                envs,
                                ki_path
                            )
                            envs = dict(_envs, **envs)
                except Exception as e:
                    self.logger.debug(traceback.format_exc())
                    self.logger.error(e)
                finally:
                    for f in files:
                        try:
                            ssh_client.execute("rm -f {}".format(f))
                        except:
                            pass
        except Exception as e:
            self.logger.debug(traceback.format_exc())
            self.logger.error(e)

    def is_compatible_and_valid_image(self, manifest):
        if "min_version" in manifest and manifest["min_version"] > self.kindo_version:
            return False

        if "name" not in manifest or "author" not in manifest or "version" not in manifest:
            return False
        return True

    def get_ki_paths(self):
        ki_paths = []

        for option in self.options[2:]:
            ki_path = option
            if ki_path[-3:] != ".ki":
                ki_path = "%s.ki" % ki_path

            if not os.path.isfile(ki_path):
                path = os.path.realpath(ki_path)
                if not os.path.isfile(path):
                    path = os.path.join(self.startfolder, ki_path)
                    if not os.path.isfile(path) and "/" in option and ":" in option:
                        path = self.get_image_path(option)
                        if not path:
                            path = self.pull_image_path(option)

                ki_path = path

            if os.path.isfile(ki_path):
                ki_paths.append(ki_path)
        return ki_paths

    def pull_image_path(self, imagename):
        try:
            name, version = imagename.split(":") if ":"in imagename else (imagename, "")
            author, name = name.split("/") if "/" in name else ("", name)

            isok, res = self.api.pull(author, name, version)
            if isok:
                path = self.download_package(res)
                if not self.add_image_info(res, path):
                    raise Exception("pull failed")
                return path
        except:
            self.logger.debug(traceback.format_exc())
        return ""

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

        cf = ConfigParser(ini_path)
        cf.set(image_info["name"], "name", image_info["name"])
        cf.set(image_info["name"], "version", image_info["version"])
        cf.set(image_info["name"], "buildtime", image_info["buildtime"])
        cf.set(image_info["name"], "maintainer", image_info["maintainer"])
        cf.set(image_info["name"], "size", image_info["size"])
        cf.set(image_info["name"], "url", image_info["url"])
        cf.set(image_info["name"], "path", path)
        cf.write()
        return True

    def get_ki_unpackage_folder(self, ki_path):
        ki_path_md5 = get_md5(ki_path)

        ki_unpackage_folder = os.path.join(self.kindo_caches_path, ki_path_md5)
        ki_length_cache_file = os.path.join(ki_unpackage_folder, "ki.cache")

        length = -1
        if os.path.isfile(ki_length_cache_file):
            with open(ki_length_cache_file, "r") as fs:
                ki_length_cache_file_content = fs.read()
                if ki_length_cache_file_content:
                    length = int(ki_length_cache_file_content)

        if not os.path.isdir(ki_unpackage_folder):
            os.makedirs(ki_unpackage_folder)

        ki_length = os.path.getsize(ki_path)
        if length == -1 or length != ki_length:
            if not self.unzip_file(ki_path, ki_unpackage_folder):
                raise Exception("unpackage failed")

            with open(ki_length_cache_file, "wb") as fs:
                fs.write(str(ki_length))
        return ki_unpackage_folder

    def get_image_path(self, section):
        ini_path = os.path.join(self.kindo_settings_path, "images.ini")
        if not os.path.isfile(ini_path):
            return ""

        cf = ConfigParser(ini_path)
        infos = cf.get()

        if section not in infos:
            return ""

        if "path" not in infos[section]:
            return ""

        return infos[section]["path"]

    def unzip_file(self, zipfilename, unziptodir):
        try:
            if not os.path.exists(unziptodir):
                os.makedirs(unziptodir)

            zfobj = zipfile.ZipFile(zipfilename)

            if "kipwd" in self.configs and self.configs["kipwd"]:
                zfobj.setpassword(self.configs["kipwd"])

            for name in zfobj.namelist():
                name = name.replace('\\', '/')

                if name.endswith('/'):
                    os.makedirs(os.path.join(unziptodir, name))
                else:
                    ext_filename = os.path.join(unziptodir, name)
                    ext_dir = os.path.dirname(ext_filename)
                    if not os.path.exists(ext_dir):
                        os.makedirs(ext_dir)

                    with open(ext_filename, 'wb') as fs:
                        fs.write(zfobj.read(name))

            return True
        except Exception:
            self.logger.debug(traceback.format_exc())
        return False

    def get_hosts_setting(self):
        ini_path = os.path.join(self.kindo_settings_path, "hosts.ini")
        if not os.path.isfile(ini_path):
            return {}

        cf = ConfigParser(ini_path)
        infos = cf.get()

        hosts = {}
        for section in infos:
            values = infos[section]
            section = section.lower()

            hosts[section] = {}
            for host in values:
                host = host.strip()
                password = values[host].strip()

                host = "%s:22" % host if host is not None and host.rfind(":") == -1 else host
                host = "root@%s" % host if host is not None and host.rfind("@") == -1 else host

                hosts[section][host] = password
        return hosts
