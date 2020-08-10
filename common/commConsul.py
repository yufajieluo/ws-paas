#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: commConsul.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/3 10:28

import time
import json
import consul
#from consul.base import Timeout
#from consul.tornado import Consul
#from tornado.ioloop import IOLoop
#from tornado.gen import coroutine

class ConsulHandler(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.conn = None
        return

    def connect(self):
        self.conn = consul.Consul(host = self.host, port = self.port)
        return

    def get_json(self, **kwargs):
        try:
            index, data = self.conn.kv.get(kwargs['key'])
            result = json.loads(data['Value']) if data else {}
        except Exception as e:
            result = {}
        return result
    
    def put(self, **kwargs):
        try:
            self.conn.kv.put(kwargs['key'], kwargs['value'])
        except Exception as e:
            pass
        return
    
    def register_service(self, **kwargs):
        try:
            self.conn.agent.service.register(
                kwargs['name'],
                address = kwargs['address'],
                port = kwargs['port'],
                tags = kwargs['tags']
            )
            result = True
        except Exception as e:
            result = False
        return result
    
    def set_maintain_on(self, **kwargs):
        self.conn.agent.service.maintenance(kwargs['service_id'], kwargs['status'], kwargs['reason'])
        return

    def get_checks(self, **kwargs):
        return self.conn.health.checks(kwargs['service'])

    def deregister_checks(self, **kwargs):
        for check in kwargs['checks']:
            self.conn.agent.check.deregister(check['check_id'])
        return

    def get_service_nodes(self, **kwargs):
        return self.conn.catalog.service(kwargs['service'])
    
    def get_node_checks(self, **kwargs):
        return self.conn.health.node(kwargs['node'])

    def get_health_nodes(self, **kwargs):
        return self.conn.health.service(kwargs['service'])

    def register_checks(self, **kwargs):
        for check in kwargs['checks']:
            if check['type'] == 'tcp':
                consul_check = consul.Check.tcp(
                    check['host'],
                    check['value'],
                    check['interval'],
                    timeout = check['timeout']
                )
            elif check['type'] == 'http':
                consul_check = consul.Check.http(
                    check['value'],
                    check['interval'],
                    timeout = check['timeout']
                )
            elif check['type'] == 'script':
                consul_check = consul.Check.script(
                    check['value'],
                    check['interval']
                )
            else:
                consul_check = None
            
            if consul_check:
                self.conn.agent.check.register(check['name'], check = consul_check, service_id = kwargs['service'])
        return

'''
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
'''
# test
if __name__ == '__main__':
    consul_handler = ConsulHandler('172.17.0.2', 8500)
    consul_handler.connect()

    #key_foo = KeyWatch('dc/test_dc_ws/dg/test_dg_ws/agent', consul_handler.conn)
    #key_foo.run()
    value = consul_handler.get_json(key = 'dc/test_dc_ws/dg/test_dg_ws/application')
    print('value is {0}'.format(value))