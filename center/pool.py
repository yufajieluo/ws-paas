#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: pool.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/07/09 10:28

import time
import multiprocessing
from center.worker import Worker

class Pool(multiprocessing.Process):
    def __init__(self, **kwargs):
        super(Pool, self).__init__()
        self.name = self.__class__.__name__.lower()
        self.worker_num_min = kwargs['configs'][self.name]['min_num']
        self.worker_num_max = kwargs['configs'][self.name]['max_num']
        self.logger = kwargs['logger']
        self.lock = kwargs['lock']
        self.shm = kwargs['shm']
        self.task_queue = kwargs['queue']
        self.workers = []
        self.dismissed_workers = []
        self.kv_handler = kwargs['configs']['handler']['kv']
        self.redis_handler = kwargs['configs']['handler']['redis']
        return
    
    def create_worker(self):
        self.workers.append(
            Worker(
                task_queue = self.task_queue, 
                lock = self.lock, 
                dismiss = multiprocessing.Event(), 
                busy = multiprocessing.Event(), 
                kv_handler = self.kv_handler,
                redis_handler = self.redis_handler,
                logger = self.logger
            )
        )
        return

    def init_worker(self, **kwargs):
        for index in range(self.worker_num_min):
            self.create_worker()
        return

    def dismiss_worker(self):
        for worker in self.workers:
            if (len(self.workers) > self.worker_num_min) and (not worker.is_busy()):
                worker.set_dismiss()
                worker.join()
                self.workers.remove(worker)
                self.logger.debug('join sub pid {}'.format(worker.pid))
        return
    
    def hire_worker(self):
        while True:
            if len(self.workers) < self.worker_num_max and self.task_queue.size() > 0:
                self.create_worker()
                continue
            else:
                break
        return

    def get_worker_id(self):
        return [worker.pid for worker in self.workers]

    def run(self, **kwargs):
        self.logger.info('pool process beging')
        self.init_worker()

        while True:
            self.logger.debug('init ---- this is pool process {}, sub process is {}'.format(self.pid, self.get_worker_id()))
            #self.logger.debug('full {} num'.format(10 - self.task_queue.size()))
            #for index in range(10 - self.task_queue.size()):
            #    print('put {} to queue'.format(index))
            #    self.task_queue.put('{}'.format(index))
            #time.sleep(5)
            self.hire_worker()
            #self.logger.debug('hire ---- this is main process, sub process is {0}'.format(self.get_worker_id()))
            #time.sleep(10)
            self.dismiss_worker()
            #self.logger.debug('dismiss ---- this is main process, sub process is {0}'.format(self.get_worker_id()))
            time.sleep(10)
        return