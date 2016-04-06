#!/usr/bin/env python
#-*- coding: utf-8 -*-


class ConfigParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.configs = {}

        with open(filepath, "rb") as fs:
            last_section_name = ""

            for line in fs:
                line = line.decode("utf-8").strip().replace(r"\n", "").replace(r"\r", "")
                if not line:
                    continue

                if line[0] == "[" and line[-1] == "]":
                    last_section_name = line[1:len(line) - 1].strip()
                    self.configs[last_section_name] = {}
                    continue

                if not last_section_name:
                    last_section_name = "default"
                    self.configs[last_section_name] = {}

                pos = line.find("=")
                if pos == -1:
                    self.configs[last_section_name][line] = ""
                else:
                    key = line[:pos].strip()
                    value = line[pos + 1:].strip()

                    self.configs[last_section_name][key] = value

    def get(self, section=None, key=None):
        if section is None:
            return self.configs

        if section not in self.configs:
            return None

        if key is None:
            return self.configs[section]

        if key not in self.configs[section]:
            return None

        return self.configs[section][key]

    def set(self, section, key, value):
        self.configs[section][key] = value

    def remove(self, section=None, key=None):
        if section is None:
            self.configs = {}

        if section not in self.configs:
            return

        if key is None:
            del self.configs[section]
            return

        del self.configs[section][key]

    def write(self, target=None):
        if target is None:
            target = self.filepath

        content = ""
        for section in self.configs:
            content += """
[%s]\r\n
""" % section

            for k, v in self.configs[section].items():
                content += "%s=%s\r\n" % (k, v)

        with open(target, "wb") as fs:
            fs.write(content.encode("utf-8"))
