#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import division
import urllib
from progressbar import *

def download_with_progressbar(url, target):
    pbar = ProgressBar().start()

    def progress_reporthook(block_count, block_size, total_size):
        pbar.update(int((block_count * block_size / total_size) * 100))

    urllib.urlretrieve(url, target, reporthook=progress_reporthook)
    pbar.finish()
