#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: work.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/07/09 10:28

import os
import time
import multiprocessing

class Worker(multiprocessing.Process):
    def __init__(self, **kwargs):
        super(Worker, self).__init__()
        self.task_queue = kwargs['task_queue']
        self.lock = kwargs['lock']
        self.dismiss = kwargs['dismiss']
        self.busy = kwargs['busy']
        self.kv_handler = kwargs['kv_handler']
        self.redis_handler = kwargs['redis_handler']
        self.logger = kwargs['logger']

        self.daemon = True
        self.start()
        return
    
    def run(self):
        while True:
            if self.is_dismiss():
                self.logger.debug('process {} parent {} dismiss break'.format(self.pid, self._parent_pid))
                break
            else:
                self.set_busy()
                self.lock.acquire()
                
                task = self.task_queue.get()
                if task:
                    self.logger.debug('process {} parent {} task is {}'.format(self.pid, self._parent_pid, task))
                    result = task.call_able(
                        domain = task.kwargs['domain'],
                        model = task.kwargs['model'],
                        notify_redis = task.kwargs['notify_redis'],
                        msg = task.kwargs['request_body'],
                        kv_handler = self.kv_handler, 
                        redis_handler = self.redis_handler, 
                        logger = self.logger
                    )
                    # result queue

                self.lock.release()
                self.clear_busy()
                time.sleep(1)
                continue
        time.sleep(2)
        return

    def set_dismiss(self):
        self.dismiss.set()
        return

    def clear_dismiss(self):
        self.dismiss.clear()
        return
    
    def is_dismiss(self):
        return self.dismiss.is_set()
    
    def set_busy(self):
        self.busy.set()
        return

    def clear_busy(self):
        self.busy.clear()
        return

    def is_busy(self):
        return self.busy.is_set()