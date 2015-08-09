#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys

class ArgsParse:
    def __init__(self, argv, skip=0):
        self.argv = argv
        self.skip = skip
        self.options = {}

    def add_option(self, group, description=None, short_name=None, long_name=None, dest=None, default=None, help=None):
        if short_name is None and long_name is None:
            return

        if dest is None:
            if long_name is not None:
                dest = long_name
            elif short_name is not None:
                dest = short_name

        if group not in self.options:
            self.options[group] = {"description": "" if description is None else description, "options": []}

        self.options[group]["options"].append(
            {
                "short_name": short_name,
                "long_name": long_name,
                "dest": dest,
                "default": default,
                "help": "" if help is None else help
            }
        )

    def parse_args(self):
        args, options, last_key = {}, [], None
        for argc in self.argv[self.skip:]:
            if last_key is not None and argc[0] != "-":
                args[last_key] = argc
                last_key = None
            elif last_key is not None and argc[:2] == "--":
                args[last_key] = ""
                if len(argc) > 2:
                    last_key = argc[2:]
            elif last_key is not None and argc[0] == "-":
                args[last_key] = ""
                if len(argc) > 2:
                    args[argc[1]] = argc[2:]
                    last_key = None
                else:
                    last_key = argc[1]
            elif last_key is None and argc[0] != "-":
                options.append(argc)
            elif last_key is None and len(argc) > 2 and argc[:2] == "--":
                last_key = argc[2:]
            elif last_key is None and len(argc) > 1 and argc[0] == "-" and argc[1] != "-":
                if len(argc) > 2:
                    args[argc[1]] = argc[2:]
                else:
                    last_key = argc[1]

        if last_key is not None:
            args[last_key] = ""


        args_parsed = {}
        for arg_k, arg_v in args.items():
            is_parsed = False
            for k, v in self.options.items():
                for option in v["options"]:
                    if option["short_name"] is not None and arg_k == option["short_name"]:
                        args_parsed[option["dest"]] = option["default"] if not arg_v else arg_v
                        is_parsed = True
                    elif option["long_name"] is not None and arg_k == option["long_name"]:
                        args_parsed[option["dest"]] = option["default"] if not arg_v else arg_v
                        is_parsed = True
            if not is_parsed:
                args_parsed[arg_k] = arg_v


        return options, args_parsed

    def show_help(self):
        banner = """
Usage: %s [options]

""" % sys.argv[0]

        for k, v in self.options.items():
            command_banner = """
%s:
    %s
"""
            for option in v["options"]:
                option_k = "-%s" % option["short_name"]
                if option["long_name"] is not None:
                    option_k = "--%s" % option["long_name"]

                option_banner = """
     %s=%s      %s
""" % (option_k, option["dest"], option["help"])

                command_banner += option_banner

            banner += command_banner

        return banner
