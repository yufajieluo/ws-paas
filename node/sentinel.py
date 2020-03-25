#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: sentinel.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/2 10:28

import os
import sys
import time
import threading
import multiprocessing
from .rapidReaction import RapidReaction
from common.commLog import LogHandler
from common.commConsul import ConsulWatch

class Sentinel(object):
    def __init__(self, logger, configs):
        self.logger = logger
        self.shm = None
        self.watch_keys = configs['consul']['watchs']
        for watch_key in self.watch_keys:
            watch_key['key'] = watch_key['key'].replace(
                'DC_NAME', configs['default']['dc_name']).replace(
                'DG_NAME', configs['default']['dg_name']
            )

        self.watch_processes = []

        self.kv_handler = configs['handler']['kv']
        self.kv_watch = configs['watch']['class']

        self.rapid_reaction = RapidReaction(logger)
        self.logger_handler = LogHandler(configs['logging'])
        return

    def register_watch_keys(self):
        for watch_key in self.watch_keys:
            watch_key_logger = self.logger_handler.register_rotate(watch_key['func'])
            key_watch_obj = eval(
                '{0}(\
                    type = watch_key[\'type\'], \
                    key = watch_key[\'key\'], \
                    handler = self.kv_handler, \
                    call_func = self.rapid_reaction.qrf, \
                    qrf_func = watch_key[\'func\']\
                )'.format(self.kv_watch)
            )
            #key_watch_obj = Watch(
            #    watch_key['key'],
            #    self.kv_handler,
            #    self.rapid_reaction.qrf,
            #    watch_key['func']
            #)
            process_watch = multiprocessing.Process(
                target = key_watch_obj.run,
                name = watch_key['key'],
                kwargs = {'logger': watch_key_logger, 'shm': self.shm}
            )
            self.watch_processes.append(process_watch)
        return

    def process(self, **kwargs):
        self.shm = kwargs['shm']
        self.register_watch_keys()
        for process in self.watch_processes:
            process.start()
        
        while True:
            self.logger.debug('this is sentinel main process...')
            time.sleep(10)
        