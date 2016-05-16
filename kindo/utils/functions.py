#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import division
import os
import re
import hashlib
import urllib
import zipfile
from kindo.utils.progressbar import *


def download_with_progressbar(url, target):
    target_dir = os.path.dirname(target)
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)

    pbar = ProgressBar().start()

    def progress_reporthook(block_count, block_size, total_size):
        progress = int((block_count * block_size / total_size) * 100)
        if progress > 100:
            return
        pbar.update(progress)

    urllib.request.urlretrieve(url, target, reporthook=progress_reporthook)

    pbar.finish()


def get_md5(value):
    hash = hashlib.md5()
    hash.update(value)
    return hash.hexdigest()


def get_files_info(directory):
    if not os.path.isdir(directory):
        return []

    files_info = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            files_info.append(
                {"name": filename, "url": os.path.join(dirpath, filename)}
            )

        for dirname in dirnames:
            subdir = os.path.join(dirpath, dirname)
            files_info.extend(get_files_info(subdir))
    return files_info


def get_content_parts(content):
    if not content:
        return []

    if content[0] == "\"":
        content = " %s" % content

    if content[-1] == "\"":
        content = "%s " % content

    parts = [part for part in content.split("\"") if part.strip() != ""]
    if not parts:
        return []

    new_parts = []
    for part in parts:
        quote_value_pattern_first = "\s+\"\s*%s\s*\"\s+" % part
        quote_value_pattern_second = "=\"\s*%s\s*\"\s+" % part
        if len(re.findall(quote_value_pattern_first, content)) > 0:
            new_parts.append(part)
        elif len(re.findall(quote_value_pattern_second, content)) > 0:
            new_parts.append(part)
        else:
            new_parts += [p for p in part.split(" ") if p.strip() != ""]
    return new_parts


def unzip_to_folder(zip_path, folder, name=None, pwd=None):
    if not os.path.isfile(zip_path):
        return False

    if not os.path.exists(folder):
        os.makedirs(folder)

    zfobj = zipfile.ZipFile(zip_path)

    if pwd is not None:
        zfobj.setpassword(pwd)

    for zfname in zfobj.namelist():
        zfname = zfname.replace('\\', '/')

        if zfname.endswith('/'):
            os.makedirs(os.path.join(folder, zfname))
            continue

        if name is not None and name != zfname:
            continue

        ext_filename = os.path.join(folder, zfname)
        ext_dir = os.path.dirname(ext_filename)
        if not os.path.exists(ext_dir):
            os.makedirs(ext_dir)

        with open(ext_filename, 'wb') as fs:
            fs.write(zfobj.read(zfname))

    return True
