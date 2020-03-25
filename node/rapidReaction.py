#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: rapidReaction.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/4 10:28

import json
import inspect
from .agent import Agent

class RapidReaction(object):
    def __init__(self, logger):
        self.logger = logger
        return

    def qrf(self, **kwargs):
        func_name = 'qrf_{0}'.format(kwargs['func'])
        cls_funcs = inspect.getmembers(self, callable)
        if func_name not in [cls_func[0] for cls_func in cls_funcs]:
            self.logger.error(
                'key {0} qrf function {1} not found, please check configuration.'.format(
                    kwargs['key'], 
                    kwargs['func']
                )
            )
        else:
            eval('self.{0}'.format(func_name))(
                type = kwargs['type'],
                value = kwargs['value'],
                shm = kwargs['shm'],
                logger = kwargs['logger']
            )
        return
    
    def qrf_dg_info(self, **kwargs):
        kwargs['logger'].debug('this is {0}, value is {1}'.format(inspect.stack()[0][3], kwargs['value']))
        if kwargs['type'] in kwargs['shm']['queue'].keys():
            kwargs['shm']['queue'][kwargs['type']].put(kwargs['value'], 5)
        return

    def qrf_dg_agent(self, **kwargs):
        kwargs['logger'].debug('this is {0}, value is {1}'.format(inspect.stack()[0][3], kwargs['value']))
        #kwargs['shm']['kv']['agent'] = json.loads(kwargs['value'])
        return