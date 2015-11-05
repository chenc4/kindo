#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import tempfile
from utils.configParser import ConfigParser


class KindoCore():
    def __init__(self, startfolder, configs, options, logger):
        self.startfolder = startfolder
        self.configs = configs
        self.options = options
        self.logger = logger

        self.kindo_version = "1.0"
        self.kindo_api_version = "1.0"
        self.kindo_tmps_path = os.path.join(tempfile.gettempdir(), "kindo")
        self.kindo_caches_path = os.getenv("KINDO_CACHES_PATH")
        self.kindo_kics_path = os.getenv("KINDO_KICS_PATH")
        self.kindo_images_path = os.getenv("KINDO_IMAGES_PATH")
        self.kindo_settings_path = os.getenv("KINDO_SETTINGS_PATH")

        if self.kindo_caches_path is None:
            if os.getenv("APPDATA") is None:
                if os.path.isdir("/var/cache"):
                    self.kindo_caches_path = "/var/cache/kindo"
                else:
                    self.kindo_caches_path = os.path.join(self.kindo_tmps_path, "caches")
            else:
                self.kindo_caches_path = os.path.join(os.getenv("APPDATA"), "kindo", "caches")

        if self.kindo_kics_path is None:
            confs_path = os.path.join(self.startfolder, "kics")
            if not os.path.isdir(confs_path):
                if os.getenv("APPDATA") is None:
                    if os.path.isdir("/var/opt"):
                        self.kindo_kics_path = "/var/opt/kindo/kics"
                    else:
                        self.kindo_kics_path = os.path.join(self.kindo_tmps_path, "kics")
                else:
                    self.kindo_kics_path = os.path.join(os.getenv("APPDATA"), "kindo", "kics")
            else:
                self.kindo_kics_path = confs_path

        if self.kindo_images_path is None:
            images_path = os.path.join(self.startfolder, "images")
            if not os.path.isdir(images_path):
                if os.getenv("APPDATA") is None:
                    if os.path.isdir("/var/opt"):
                        self.kindo_images_path = "/var/opt/kindo/images"
                    else:
                        self.kindo_images_path = os.path.join(self.kindo_tmps_path, "images")
                else:
                    self.kindo_images_path = os.path.join(os.getenv("APPDATA"), "kindo", "images")
            else:
                self.kindo_images_path = images_path

        if self.kindo_settings_path is None:
            settings_path = os.path.join(self.startfolder, "settings")
            if not os.path.isdir(settings_path):
                if os.getenv("APPDATA") is None:
                    if os.path.isdir("/etc/opt"):
                        self.kindo_settings_path = "/etc/opt/kindo"
                    else:
                        self.kindo_settings_path = os.path.join(self.kindo_tmps_path, "settings")
                else:
                    self.kindo_settings_path = os.path.join(os.getenv("APPDATA"), "kindo", "settings")
            else:
                self.kindo_settings_path = settings_path

        self.configs = dict(self.get_kindo_setting(), **self.configs)

    def get_kindo_setting(self):
        ini_path = os.path.join(self.kindo_settings_path, "kindo.ini")
        if not os.path.isfile(ini_path):
            return {}

        cf = ConfigParser()
        cf.read(ini_path)

        configs = {}
        for section in cf.sections():
            items = cf.items(section)
            section = section.lower()

            for k, v in items:
                k = k.strip()
                v = v.strip()
                configs[k] = v
        return configs

    def set_kindo_setting(self, key, value):
        ini_path = os.path.join(self.kindo_settings_path, "kindo.ini")
        if not os.path.isdir(self.kindo_settings_path):
            os.makedirs(self.kindo_settings_path)

        if not os.path.isfile(ini_path):
            with open(ini_path, "w") as fs:
                fs.write("[default]")

        cf = ConfigParser()
        cf.read(ini_path)

        cf.set("default", key, value)
        cf.write(open(ini_path, "w"))



