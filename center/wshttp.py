#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: wshttp.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/2 10:28

import sys
import time
import json
import tornado.web
import tornado.ioloop
import multiprocessing
from tornado import gen

from center.task import Task
from center.mission import Mission

class Wshttp(multiprocessing.Process):
    def __init__(self, **kwargs):
        super(Wshttp, self).__init__()
        self.app = None
        self.name = self.__class__.__name__.lower()
        self.port = kwargs['configs'][self.name]['port']
        self.logger = kwargs['logger']
        self.urls = kwargs['configs'][self.name]['urls']
        self.task_queue = kwargs['queue']
        
        self.mission = Mission(
            urls = self.urls,
            single_timeout = kwargs['configs']['wshttp']['single_timeout'],
            kv_key_dc = kwargs['configs']['kv']['key_dc'],
            kv_key_dg = kwargs['configs']['kv']['key_dg'],
            redis_key = kwargs['configs']['redis']['key']
        )
        
        self.request_map = {}
        self.init_request_map()
        return

    def init_request_map(self):
        for url in self.urls:
            key_dict = {}
            for method in url['methods']:
                try:
                    key_dict[method.lower()] = eval('self.mission.process_{}'.format(method.lower()))
                except Exception as e:
                    self.logger.error('init request map Exception: {}'.format(e))
                    continue
            self.request_map[url['name']] = key_dict
        return

    def make_app(self):
        handlers = []
        for url in self.urls:
            try:
                handlers.append(
                    eval(
                        ''' \
                        ( \
                            url['url'], \
                            {}Handler,  \
                            {{
                                'urls': self.urls, \
                                'logger': self.logger, \
                                'request_map': self.request_map, \
                                'task_queue': self.task_queue \
                            }} \
                        ) \
                        '''.format('Template')
                    )
                )
            except NameError as e:
                self.logger.error('Exception: {0}'.format(e))
        
        self.app = tornado.web.Application(
            handlers,
            autoreload = True
        )
    
    def run(self, **kwargs):
        self.make_app()
        self.app.listen(self.port)
        tornado.ioloop.IOLoop.current().start()
        print('---------1')

class TemplateHandler(tornado.web.RequestHandler):
    def initialize(self, **kwargs):
        self.urls = kwargs['urls']
        self.request_map = kwargs['request_map']
        self.task_queue = kwargs['task_queue']
        self.logger = kwargs['logger']
        return
    
    def accept_request(self, **kwargs):
        result = False

        for url in self.urls:
            if url['url'] == kwargs['url']:
                domain = url['domain']
                notify_redis = url['notify_redis']

                task = Task(
                    call_able = self.request_map[url['name']][kwargs['method']], 
                    kwargs = {
                        'domain': domain,
                        'model': url['url'].split('/')[-1] if url['url'].split('/')[-1] else url['url'].split('/')[-2],
                        'notify_redis': notify_redis,
                        'request_body': kwargs['kwargs']
                    }
                )
                
                for index in range(3):
                    if self.task_queue.full():
                        self.logger.info('task queue full, wait 1 second.')
                        continue
                    else:
                        self.task_queue.put(task)
                        result = True
                        break
                
                break

        return result
    
    async def put(self):
         self.logger.debug('{} {}'.format(self.request.method, self.request.uri))
         self.accept_request(
             url = self.request.uri,
             method = self.request.method.lower(),
             kwargs = json.loads(self.request.body)
         )
         self.finish({'echo': '{} {} echo'.format(self.request.method, self.request.uri)})