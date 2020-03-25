#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: commPress.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/12 10:28

import os

class PressHandler(object):
    def __init__(self):
        return
    
    def commpress(self, **kwargs):
        if os.path.isfile(kwargs['target']):
            with tarfile.open(kwargs['tarfile'], 'w:gz') as tar_handler:
                tar_handler.add(kwargs['target'])
            result = True
        elif os.path.isdir(kwargs['target']):
            with tarfile.open(kwargs['tarfile'], 'w:gz') as tar_handler:
                for root, dirs, files in os.walk(kwargs['target']):
                    for file in files:
                        tar_handler.add(os.path.join(root, file))
            result = True
        else:
            result = False
        return result
    
    def uncommpress(self, **kwargs):
        if os.path.isfile(kwargs['tarfile']):
            with tarfile.open(kwargs['tarfile'], 'r') as tar_handler:
                tar_handler.extractall(path = kwargs['tarpath'])
            result = True
        else:
            result = False
        return result