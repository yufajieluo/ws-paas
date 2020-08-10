#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: task.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/07/15 22:38

class Task(object):
    def __init__(self, call_able = None, callback = None, exception_callback = None, args = None, kwargs = None):
        self.id = id(self)
        self.args = args
        self.kwargs = kwargs
        self.exception = False
        self.callback = callback
        self.exception_callback = exception_callback
        self.call_able = call_able
        return

    def __str__(self):
        return 'Task id = {} kwargs = {}'.format(self.id, self.kwargs)