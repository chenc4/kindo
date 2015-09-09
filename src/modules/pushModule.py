#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import traceback
import requests
import hashlib
import zipfile
import simplejson
from modules.kindoModule import KindoModule


class PushModule(KindoModule):
    def __init__(self, command, startfolder, configs, options, logger):
        KindoModule.__init__(self, command, startfolder, configs, options, logger)

    def start(self):
        push_engine_url = "%s/v1/push" % self.configs.get("index", "kindo.cycore.cn")
        if push_engine_url[:7].lower() != "http://" and push_engine_url[:8].lower() != "https://":
            push_engine_url = "http://%s" % push_engine_url

        for option in self.options[2:]:
            try:
                package_path = self.get_package_path(option)
                if not package_path or not os.path.isfile(package_path):
                    self.logger.warn("\"%s\" not found" % option)
                    continue

                self.logger.info("pushing %s" % option)

                code = self.configs.get("code", "")
                if code and len(code) != 6:
                    self.logger.error("only six characters are allowed")
                    return

                data = {"code": code}
                if "username" in self.configs:
                    data["username"] = self.configs["username"]
                    data["author"] = self.configs["username"]

                if "password" in self.configs:
                    data["token"] = hashlib.new("md5", self.configs["password"]).hexdigest()

                cache_folder = self.get_cache_folder(package_path)
                if not self.unzip_file(package_path, cache_folder):
                    self.logger.warn("UNPACKAGE FAILED: %s" % package_path)
                    continue

                manifest_path = "%s/manifest.json" % cache_folder
                if os.path.isfile(manifest_path):
                    manifest = simplejson.load(open(manifest_path, "r"))
                    data["author"] = manifest.get("author", data["username"])
                    if data["author"] == "anonymous":
                        data["author"] = data["username"]

                    data["version"] = manifest.get("version", "1.0")
                    data["name"] = manifest.get("name", "")
                    data["website"] = manifest.get("website", "")
                    data["summary"] = manifest.get("summary", "")
                    data["license"] = manifest.get("license", "")
                    data["buildversion"] = manifest.get("buildversion", "")
                    data["buildtime"] = manifest.get("buildtime", "")

                self.logger.info("connecting %s" % push_engine_url)
                self.logger.debug(data)
                r = requests.post(push_engine_url, data=data, files={"file": open(package_path, "rb")})
                if r.status_code != 200:
                    self.logger.error("\"%s\" can't connect" % push_engine_url)
                    return

                response = r.json()

                if "code" in response:
                    self.logger.error(response["msg"])
                    return

                self.logger.response("pushed %s" % option)
            except:
                self.logger.debug(traceback.format_exc())
                self.logger.error("\"%s\" can't connect" % push_engine_url)

    def get_package_path(self, name):
        kiname = name if name[-3:] == ".ki" else "%s.ki" % name
        self.logger.info("finding %s" % kiname)
        if os.path.isfile(kiname):
            self.logger.info("finded %s" % kiname)
            return kiname

        path = os.path.realpath(kiname)
        self.logger.info("finding %s" % path)
        if os.path.isfile(path):
            self.logger.info("finded %s" % path)
            return path

        path = os.path.join(self.startfolder, kiname)
        self.logger.info("finding %s" % path)
        if os.path.isfile(path):
            self.logger.info("finded %s" % path)
            return path

        path = os.path.join(self.startfolder, "images", kiname)
        self.logger.info("finding %s" % path)
        if os.path.isfile(path):
            self.logger.info("finded %s" % path)
            return path

        path = self.get_image_path(name)
        self.logger.info("finding %s" % path)
        if os.path.isfile(path):
            self.logger.info("finded %s" % path)
            return path

        name, version = name.split(":") if ":"in name else (name, "")
        author, name = name.split("/") if "/" in name else ("", name)

        kiname = "anonymous-%s" % name if not author else "%s-%s" % (author, name)
        kiname = "%s-1.0" % kiname if not version else "%s-%s" % (kiname, version)

        path = self.get_image_path(kiname)
        self.logger.info("finding %s" % path)
        if os.path.isfile(path):
            self.logger.info("finded %s" % path)
            return path

        return ""

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

    def get_cache_folder(self, filepath):
        # for example: /var/cache/kindo/nginx/nginx-1.0.0
        folder, filename = os.path.split(filepath)
        whole_name, ext = os.path.splitext(filename)
        last_hyphen_pos = whole_name.rfind("-")
        name = whole_name if last_hyphen_pos == -1 else whole_name[:last_hyphen_pos]

        return os.path.join(self.kindo_caches_path, name, whole_name)

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
