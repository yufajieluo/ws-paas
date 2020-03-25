#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: commYaml.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/4 10:28

import yaml

class YamlHandler(object):
    def __init__(self):
        return
    
    def loads(self, file):
        content = None
        try:
            with open(file) as file_handler:
                content = yaml.safe_load(file_handler)
        except:
            pass
        return content

if __name__ == '__main__':
    yaml_handler = YamlHandler()
    print(yaml_handler.loads('../config/node.yaml'))