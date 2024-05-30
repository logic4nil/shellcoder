# -*- coding: UTF-8 -*-
"""
本文件提供了YAML文件解析

Authors: logic4nil(logic4nil@gmail.com)
Date:    2024/05/20 15:22:39
"""
import os

import yaml

class ConfigLoader(object):
    def __init__(self):
        self._envs = {}
        self._functions = {}
        self._tasks = []
        self._loaded = []

    def _load_yaml_file(self, yaml_file):
        yaml_file = os.path.realpath(os.path.abspath(yaml_file))
        yaml_dir = os.path.dirname(yaml_file)
        if yaml_file in self._loaded:
            return
        else:
            self._loaded.append(yaml_file)

        with open(yaml_file, "r") as file:
            config = yaml.safe_load(file)

            if 'include' in config:
                for inclu in config['include']:
                    if not os.path.isabs(inclu):
                        inclu = os.path.join(yaml_dir, inclu)
                    self._load_yaml_file(inclu)

            if 'env' in config:
                self._envs.update(config['env'])

            if 'functions' in config:
                for func_name, func_script in config['functions'].items():
                    if func_name == "init":
                        self._functions["init"] = self._functions.get("init", "") + "\n" + func_script
                    else:
                        self._functions[func_name] = func_script

            if 'tasks' in config:
                self._tasks.extend(config['tasks'])

    def load(self, yaml_files):
        for yaml_file in yaml_files:
            self._load_yaml_file(yaml_file)

    def envs(self):
        return self._envs

    def functions(self):
        return self._functions

    def tasks(self):
        return self._tasks
