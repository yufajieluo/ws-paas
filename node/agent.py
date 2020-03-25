#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: agent.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/9 10:28

import os
import time
from .template import Template

class Agent(Template):
    def process(self, **kwargs):
        self.logger.info('It\'s my turn finally agent!')
        
        while True:
            self.logger.debug('this is agent main process...')
            self.logger.debug('shm is {0}'.format(kwargs['shm']))
            #kwargs['shm']['status']['agent'] = 'active'
            #value = self.kv_handler.get_key(self.key)
            time.sleep(10)

        return