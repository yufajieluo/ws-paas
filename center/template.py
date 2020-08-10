#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: template.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/07/23 21:59

import asyncio

class Template(object):
    def __init__(self, **kwargs):
        self.logger = kwargs['logger']
        self.config = kwargs['configs']
        self.shm = kwargs['shm']
        self.lock = kwargs['lock']
        self.queue = kwargs['queue']
        self.dependent = kwargs['dependent']

        self.name = self.__class__.__name__.lower()
        return

    def is_switch(self, **kwargs):
        return self.shm['status'][self.name]['intime'] == 'normal' and \
               self.shm['status'][self.name]['expect'] == 'normal'
        
    def switch_on(self, **kwargs):
        self.lock.acquire()
        shm_status = self.shm['status']
        shm_status[self.name]['intime'] = 'normal'
        self.shm['status'] = shm_status
        self.lock.release()
        return
    
    def switch_off(self, **kwargs):
        self.lock.acquire()
        shm_status = self.shm['status']
        shm_status[self.name]['intime'] = 'pending'
        self.shm['status'] = shm_status
        self.lock.release()
        return

    def levy(self, **kwargs):
        self.lock.acquire()
        shm_status = self.shm['status']

        for key in shm_status.keys():
            if key != self.name:
                shm_status[key]['expect'] = 'pending'
        
        self.shm['status'] = shm_status
        self.lock.release()
        return
    
    def is_levy(self, **kwargs):
        return self.shm['status'][self.name]['expect'] == 'pending'

    def disband(self, **kwargs):
        self.lock.acquire()
        shm_status = self.shm['status']

        for key in shm_status.keys():
            if key != self.name:
                shm_status[key]['intime'] = 'normal'
                shm_status[key]['expect'] = 'normal'
        
        self.shm['status'] = shm_status
        self.lock.release()
        return
    
    def enlist(self, **kwargs):
        self.lock.acquire()
        shm_status = self.shm['status']
        shm_status[self.name]['intime'] = 'ready'
        self.shm['status'] = shm_status
        self.lock.release()
        return

    def is_reunify(self, **kwargs):
        is_reunify = True
        for key in self.shm['status'].keys():
            if key != self.name:
                if self.shm['status'][key]['intime'] != 'ready':
                    is_reunify = False
                    break
        return is_reunify

    def shutdown(self, **kwargs):
        self.lock.acquire()
        self.shm['running'] = False
        self.lock.release()
        return
    
    async def watcher(self, **kwargs):
        while True:
            self.logger.debug('this is watcher')
            if self.is_levy():
                self.enlist()
                await asyncio.sleep(5)
            else:
                if self.is_switch():
                    self.worker()
                await asyncio.sleep(5)
        return
    
    async def whisper(self, **kwargs):
        while True:
            self.logger.debug('this is {0} whisper.'.format(self.name))
            self.logger.debug('shm status is {0}'.format(self.shm))
            self.get_current_version()
            if not self.version:
                self.init = True
                self.logger.info('start up with no version on {0}, init default version.'.format(self.name))
                value = self.kv_handler.get_json(key = self.kv_key)
                self.logger.debug('kv key is {0}, value is {1}'.format(self.kv_key, value))
                self.worker(msg = value)
            self.logger.info('service {0} current version is {1}'.format(self.appname, self.version))
            
            if self.version and self.appname:
                self.init = False
            await asyncio.sleep(5)
        return
    
    def run(self, **kwargs):
        loop = asyncio.get_event_loop()
        loop_tasks = []
        loop_tasks.append(loop.create_task(self.whisper()))
        loop_tasks.append(loop.create_task(self.watcher()))
        loop.run_until_complete(asyncio.wait(loop_tasks))
        return
    
    # waiting for reload
    def worker(self, **kwargs):
        return