#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import tempfile

from . import KINDO_VERSION, KINDO_MIN_VERSION, KINDO_API_VERSION, KINDO_DEFAULT_HUB_HOST
from kindo.utils.config_parser import ConfigParser
from kindo.plugins.kindohub.plugin import Plugin as KindoHubPlugin


class KindoCore():
    def __init__(self, startfolder, configs, options, logger):
        self.startfolder = startfolder
        self.configs = configs
        self.options = options
        self.logger = logger

        self.kindo_version = KINDO_VERSION
        self.kindo_min_version = KINDO_MIN_VERSION
        self.kindo_api_version = KINDO_API_VERSION
        self.kindo_default_hub_host = KINDO_DEFAULT_HUB_HOST
        self.kindo_tmps_path = os.path.join(tempfile.gettempdir(), "kindo")
        self.kindo_caches_path = os.getenv("KINDO_CACHES_PATH")
        self.kindo_kics_path = os.getenv("KINDO_KICS_PATH")
        self.kindo_images_path = os.getenv("KINDO_IMAGES_PATH")
        self.kindo_settings_path = os.getenv("KINDO_SETTINGS_PATH")
        self.plugins = [KindoHubPlugin]
        self.api = None

        if self.kindo_default_hub_host[-1] == "/":
            self.kindo_default_hub_host = self.kindo_default_hub_host[:-1]

        if self.kindo_default_hub_host[:7] != "http://" and self.kindo_default_hub_host[:8] != "https://":
            self.kindo_default_hub_host = "http://%s" % self.kindo_default_hub_host

        for plugin in self.plugins:
            if plugin.is_valid_host(self.kindo_default_hub_host):
                self.api = plugin(self.kindo_default_hub_host)
                break

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

    def get_kindo_setting(self, key=None):
        ini_path = os.path.join(self.kindo_settings_path, "kindo.ini")
        if not os.path.isfile(ini_path):
            return {}

        cf = ConfigParser(ini_path)

        if key is None:
            return cf.get()
        return cf.get("default", key)

    def set_kindo_setting(self, key, value):
        ini_path = os.path.join(self.kindo_settings_path, "kindo.ini")
        if not os.path.isdir(self.kindo_settings_path):
            os.makedirs(self.kindo_settings_path)

        cf = ConfigParser(ini_path)
        cf.set("default", key, value)
        cf.write(ini_path)
