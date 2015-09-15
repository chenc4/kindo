#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import division
import urllib2
from progressbar import *

def download_with_progressbar(url, target):
    pbar = ProgressBar().start()

    u = urllib2.urlopen(url)
    total = int(u.info().getheaders("Content-Length")[0])

    file_size_dl = 0
    block_sz = 8192

    with open(target, "wb") as fs:
        while True:
            block_buffer = u.read(block_sz)
            if not block_buffer:
                break

            file_size_dl += len(block_buffer)
            fs.write(block_buffer)

            pbar.update(int((file_size_dl / total) * 100))
    pbar.finish()
