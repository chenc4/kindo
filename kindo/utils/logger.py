#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
import time
import logging
import platform
from fabric.api import env

FOREGROUND_WHITE = 0x0007
FOREGROUND_BLUE = 0x01  # text color contains blue.
FOREGROUND_GREEN = 0x02  # text color contains green.
FOREGROUND_RED = 0x04  # text color contains red.
FOREGROUND_YELLOW = FOREGROUND_RED | FOREGROUND_GREEN

if platform.system() == "Windows":
    import ctypes

    STD_OUTPUT_HANDLE = -11
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    def set_color(color, handle=std_out_handle):
        bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return bool

else:
    def std_out_handle():
        pass

    def set_color(color, handle=std_out_handle):
        pass


class Logger:
    def __init__(self, logfolder, isdebug=False):
        if not os.path.isdir(logfolder):
            os.makedirs(logfolder)

        createtime = time.strftime('%Y%m%d%H', time.localtime(time.time()))
        logfile = os.path.join(logfolder, "kindo.%s.log" % createtime)

        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')

        hdlr = logging.FileHandler(logfile)
        hdlr.setFormatter(formatter)

        slr_formatter = logging.Formatter('%(message)s', '%Y-%m-%d %H:%M:%S')
        slr = logging.StreamHandler(sys.stderr)
        slr.setFormatter(slr_formatter)

        logger = logging.getLogger()
        logger.addHandler(hdlr)
        logger.setLevel(logging.ERROR if not isdebug else logging.DEBUG)

        self.logger = logging.getLogger("kindo")
        self.logger.addHandler(hdlr)
        self.logger.addHandler(slr)
        self.logger.setLevel(logging.INFO if not isdebug else logging.DEBUG)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message, color=FOREGROUND_YELLOW):
        set_color(color)
        self.logger.warn(message)
        set_color(FOREGROUND_WHITE)

    def error(self, message, color=FOREGROUND_RED):
        set_color(color)
        self.logger.error(message)
        set_color(FOREGROUND_WHITE)

    def critical(self, message):
        self.logger.critical(message)

    def response(self, message, is_ok=True, host="127.0.0.1"):
        msg = """
%s | %s  >>

%s
""" % (host if env.host is None else env.host, "success" if is_ok else "failed", message)

        if is_ok:
            self.info(msg)
        else:
            self.error(msg)

    def response_error(self, message, short_msg, long_msg):
        msg = """
[%s] %s  >>

%s
""" % (message, short_msg, long_msg)

        self.error(msg)
