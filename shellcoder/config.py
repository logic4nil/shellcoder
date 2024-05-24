# -*- coding: UTF-8 -*-
"""
本文件提供了YAML文件解析

Authors: logic4nil(logic4nil@gmail.com)
Date:    2024/05/20 15:22:39
"""

import yaml

class ConfigLoader(object):
    def __init__(self):
        self._envs = {}
        self._functions = {}
        self._tasks = []

    def _load_yaml_file(self, yaml_file):
        with open(yaml_file, "r") as file:
            config = yaml.safe_load(file)

            if 'include' in config:
                for inclu in config['include']:
                    self._load_yaml_file(inclu)

            if 'env' in config:
                self._envs.update(config['env'])

            if 'functions' in config:
                self._functions.update(config['functions'])

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
