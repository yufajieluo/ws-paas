#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: commFile.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/2 10:28

import os
import pickle

class commFile(object):
    def __init__():
        return

    def dump(self, dump_file, dump_content):
        with open(dump_file, 'wb') as file_handler:
            pickle.dump(dump_content, file_handler)
        return
    
    def loads(self, load_file):
        with open(load_file, 'rb') as file_handler:
            load_content = pickle.load(file_handler)
        return load_file