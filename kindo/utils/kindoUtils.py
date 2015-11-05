#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import division
import os
from utils.urllib import urlretrieve
from utils.progressbar import *

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

    urlretrieve(url, target, reporthook=progress_reporthook)

    pbar.finish()
