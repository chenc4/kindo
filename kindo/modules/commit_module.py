#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import shutil
import traceback
import zipfile
import simplejson

from kindo.kindo_core import KindoCore
from kindo.utils.config_parser import ConfigParser


class CommitModule(KindoCore):
    def __init__(self, startfolder, configs, options, logger):
        KindoCore.__init__(self, startfolder, configs, options, logger)

        self.ki_path = self.get_ki_path()

    def start(self):
        if not os.path.isfile(self.ki_path):
            self.logger.response("ki not found: %s" % self.ki_path, False)
            return

        try:
            dirname, filename = os.path.split(self.ki_path)

            # unzip package and rezip to new package

            ki_output_path, manifest = self.create_new_image()

            if not self.add_image_info(manifest, ki_output_path):
                self.logger.response("commit failed", False)
                return
            self.logger.response("commit ok")
        except Exception:
            self.logger.debug(traceback.format_exc())
            self.logger.response("commit failed", False)

    def add_image_info(self, image_info, path):
        if not path:
            return False

        ini_path = os.path.join(self.kindo_settings_path, "images.ini")
        if not os.path.isdir(self.kindo_settings_path):
            os.makedirs(self.kindo_settings_path)

        cf = ConfigParser()
        cf.read(ini_path)

        sections = cf.sections()

        section = "%s/%s:%s" % (image_info["author"], image_info["name"], image_info["version"])
        if section not in sections:
            cf.add_section(section)
        cf.set(section, "name", image_info["name"])
        cf.set(section, "author", image_info["author"])
        cf.set(section, "version", image_info["version"])
        cf.set(section, "buildtime", image_info["buildtime"])
        cf.set(section, "pusher", image_info["pusher"])
        cf.set(section, "size", os.path.getsize(path))
        cf.set(section, "url", "")
        cf.set(section, "path", path)

        cf.write(open(ini_path, "w"))
        return True

    def create_new_image(self):
        dirname, filename = os.path.split(self.ki_path)
        cache_folder = self.get_cache_info(filename)
        if os.path.isdir(cache_folder):
            shutil.rmtree(cache_folder)

        if not self.unzip_file(self.ki_path, cache_folder):
            raise Exception("unpackage error")

        manifest_path = os.path.join(cache_folder, "manifest.json")

        self.logger.debug(manifest_path)
        manifest = simplejson.load(open(manifest_path, "r"))

        if "t" in self.configs:
            tag = self.configs["t"]
            name, version = tag.split(":") if ":"in tag else (tag, manifest["version"])
            author, name = name.split("/") if "/" in name else (manifest["author"], name)

            manifest["author"] = author
            manifest["version"] = version
            manifest["name"] = name

        manifest["pusher"] = self.configs.get("username", "")

        simplejson.dump(manifest, open(manifest_path, "w"))

        ki_output_path = os.path.join(self.kindo_images_path, "%s-%s-%s.ki" % (
            manifest["author"],
            manifest["name"],
            manifest["version"]
        ))
        if not os.path.isdir(self.kindo_images_path):
            os.makedirs(self.kindo_images_path)

        self.zip_dir(cache_folder, ki_output_path)

        return ki_output_path, manifest

    def get_cache_info(self, filename):
        # for example: /var/cache/kindo/nginx/nginx-1.0.0
        whole_name, ext = os.path.splitext(filename)
        last_hyphen_pos = whole_name.rfind("-")
        name = whole_name if last_hyphen_pos == -1 else whole_name[:last_hyphen_pos]

        return os.path.join(self.kindo_caches_path, name, whole_name)

    def get_ki_path(self):
        self.logger.debug(self.options)

        ki_path = ""
        for option in self.options:
            ki_path = option
            if ki_path[-3:] != ".ki":
                ki_path = "%s.ki" % ki_path

            if not os.path.isfile(ki_path):
                path = os.path.realpath(ki_path)
                if not os.path.isfile(path):
                    path = os.path.join(self.startfolder, ki_path)

                    if os.path.isfile(path):
                        ki_path = path

            if os.path.isfile(ki_path):
                break

        self.logger.debug(ki_path)
        return ki_path

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
