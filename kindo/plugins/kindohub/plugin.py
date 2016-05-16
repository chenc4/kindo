#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import requests
import hashlib


class Plugin:
    def __init__(self, host):
        if host[-1] == "/":
            host = host[:-1]

        if host[:7].lower() != "http://" and host[:8].lower() != "https://":
            host = "http://%s" % host

        self.host = host

    def login(self, username, password):
        api_url = "%s/v1/login" % self.host

        try:
            r = requests.post(
                api_url,
                data={
                    "username": username,
                    "token": hashlib.new("md5", password.encode("utf-8")).hexdigest()
                }
            )
            if r.status_code != 200:
                return False, "\"%s\" can't connect" % self.host

            response = r.json()

            if "username" not in response:
                return False, "login failed"
        except Exception as e:
            return False, e
        return True, response

    def pull(self, author, name, version):
        api_url = "%s/v1/pull" % self.host

        params = {"uniqueName": name}
        if author:
            params["uniqueName"] = "%s/%s" % (author, params["uniqueName"])
        else:
            params["uniqueName"] = "anonymous/%s" % params["uniqueName"]

        if version:
            params["uniqueName"] = "%s:%s" % (params["uniqueName"], version)
        else:
            params["uniqueName"] = "%s:latest" % params["uniqueName"]

        try:
            r = requests.get(api_url, params=params)
            if r.status_code != 200:
                return False, r.text
            return True, r.json()
        except Exception as e:
            return False, e

    def push(self, kipath, info):
        api_url = "%s/v1/push" % self.host

        if not os.path.isfile(kipath):
            return False, "'%s' not existed" % kipath

        try:
            r = requests.post(api_url, data=info, files={"file": open(kipath, "rb")})
            if r.status_code != 200:
                return False, r.text
            return True, r.json()
        except Exception as e:
            return False, e

    def register(self, username, password):
        api_url = "%s/v1/register" % self.host

        try:
            r = requests.post(api_url, data={"username": username, "password": password})
            if r.status_code != 200:
                return False, r.text
        except Exception as e:
            return False, e
        return True, r.json()

    def rm(self, author, name, version, username, password):
        api_url = "%s/v1/rm" % self.host

        data = {
            "uniqueName": "%s/%s:%s" % (author, name, version),
            "username": username,
            "token": hashlib.new("md5", password.encode("utf-8")).hexdigest()
        }

        try:
            r = requests.post(api_url, data=data)
            if r.status_code != 200:
                return False, r.text
            return True, r.json()
        except Exception as e:
            return False, e

    def search(self, q):
        api_url = "%s/v1/search" % self.host

        r = requests.get(api_url, params={"q": q})
        if r.status_code != 200:
            return False, "\"%s\" can't connect" % api_url

        response = r.json()

        if "code" in response:
            return False, response["msg"]

        return True, response

    @staticmethod
    def is_valid_host(host):
        return True
