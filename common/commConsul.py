#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: commConsul.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/3 10:28


import time
from consul.base import Timeout
from consul.tornado import Consul
from tornado.ioloop import IOLoop
from tornado.gen import coroutine


class ConsulHandler(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.conn = None
        return
    def connect(self):
        self.conn = Consul(host = self.host, port = self.port)
        return

class ConsulWatch(object):
    def __init__(self, **kwargs):
        self.type = kwargs['type']
        self.key = kwargs['key']
        self.value = None
        self.consul_handler = kwargs['handler']
        self.call_func = kwargs['call_func']
        self.qrf_func = kwargs['qrf_func']
        return

    @coroutine
    def watch(self, logger, shm):
        index = None
        while True:
            try:
                index, data = yield self.consul_handler.conn.kv.get(self.key, index = index)
                if data:
                    self.value = data['Value']
                    self.call_func(
                            type = self.type,
                            key = self.key, 
                            value = self.value,
                            func = self.qrf_func,
                            shm = shm, 
                            logger = logger
                    )
            except Timeout:
                pass
            except Exception as e:
                logger.error('connect to consul Exception: {0}, reconnect alter 10s.'.format(e))
                time.sleep(10)
        return
    
    def run(self, logger, shm):
        loop = IOLoop.instance()
        loop.add_callback(self.watch, logger, shm)
        loop.start()

# test
if __name__ == '__main__':
    consul_handler = ConsulHandler('127.0.0.1', 8500)
    consul_handler.connect()

    key_foo = KeyWatch('dc/test_dc_ws/dg/test_dg_ws/agent', consul_handler.conn)
    key_foo.run()
