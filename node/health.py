#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: agent.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/05/11 10:28

import os
import json
import time
import asyncio
from .template import Template

class Health(Template):
    def __init__(self, **kwargs):
        super(Health, self).__init__(**kwargs)

        self.service = None
        self.interval = 99
        self.health = True
        self.healthy_threshold = 0
        self.unhealthy_threshold = 0
        self.unhealthy_count = 0
        self.restart_threshold = 3
        self.restart_count = 0
        return

    def get_current_health(self, **kwargs):
        yaml_file = os.path.join(self.work_path, 'appspec.yaml')
        yaml_info = self.file_handler.loads(file = yaml_file, type = 'yaml')
        for _ in range(3):
            if os.path.isfile(yaml_file):
                break
            else:
                time.sleep(5)
                continue
        try:
            self.service = yaml_info['app']['name']
            health = self.kv_handler.get_json(key = self.kv_key)
            if not health:
                health = yaml_info['app']['health']
        except Exception as e:
            self.logger.error('get health from yaml file Exception: {0}'.format(e))
            health = {}
        return health

    def register_health(self, **kwargs):
        try:
            self.interval = kwargs['health']['interval']
            self.healthy_threshold = kwargs['health']['healthy_threshold']
            self.unhealthy_threshold = kwargs['health']['unhealthy_threshold']

            checks = self.kv_handler.get_checks(service = self.service)[1]
            self.logger.debug('old checks is {0}'.format(checks))
            self.kv_handler.deregister_checks(
                checks = [{'check_id': check['CheckID']} for check in checks]
            )

            self.logger.debug('new health is {0}'.format(kwargs['health']))
            checks = []
            for check in kwargs['health']['checks']:
                if check['type'] == 'http':
                    check['value'] = check['value'].replace('PRIVATE_ADDR', self.private_addr)
                elif check['type'] == 'tcp':
                    check['host'] = check['value'].replace('PRIVATE_ADDR', self.private_addr).split(':')[0]
                    check['value'] = int(check['value'].replace('PRIVATE_ADDR', self.private_addr).split(':')[1])
                elif check['type'] == 'script':
                    check['value'] = os.path.join(self.work_path, check['value'])
                check['interval'] = '{0}s'.format(kwargs['health']['interval'])
                check['timeout'] = '{0}s'.format(kwargs['health']['timeout'])
                checks.append(check)
            self.kv_handler.register_checks(service = self.service, checks = checks)
        except Exception as e:
            self.logger.error('register checks to kv Exception: {0}'.format(e))
        return

    def check(self, **kwargs):
        try:
            if self.unhealthy_count <= self.unhealthy_threshold:
                _, nodes = self.kv_handler.get_service_nodes(service = self.service)
                #self.logger.debug('nodes is {0}'.format(nodes))
                #self.logger.debug('self.private_addr is {0}'.format(self.private_addr))
                for node in nodes:
                    if node['ServiceAddress'] == self.private_addr:
                        health = True
                        _, checks = self.kv_handler.get_node_checks(node = node['Node'])
                        #self.logger.debug('current node {0} checks is {1}'.format(node['Node'], checks))
                        for check in checks:
                            if check['Status'] != 'passing':
                                health = False
                                break
                        if health:
                            self.unhealthy_count = 0
                            self.restart_count = 0
                        else:
                            self.unhealthy_count += 1
            else:
                self.logger.error('unhealthy count {0} greater than unhealthy threshold {1}, restart service.'.format(
                    self.unhealthy_count, self.unhealthy_threshold
                ))
                if self.restart_count <= self.restart_threshold:
                    self.exec_hook(hook_name = 'restart')
                    self.unhealthy_count = 0
                    self.restart_count += 1
                else:
                    self.logger.error('restart count {0} greater than restart threshold {1}, notice.'.format(
                        self.restart_count, self.restart_threshold
                    ))
                    # notice

        except Exception as e:
            self.logger.error('exec check Exception: {0}'.format(e))
        return

    # reload
    async def whisper(self, **kwargs):
        while True:
            self.logger.debug('this is {0} whisper.'.format(self.name))
            if not self.init:
                self.logger.debug('self init is {0}'.format(self.init))
                health = self.get_current_health()
                self.register_health(health = health)
                self.init = True
            
            # check 
            if not self.is_maintain():
                self.check()
            else:
                self.unhealthy_count = 0
                self.logger.info('service is maintain, pause health check.')

            self.logger.debug('self.interval is {0}'.format(self.interval))
            await asyncio.sleep(self.interval)
        return

    # reload
    def worker(self, **kwargs):
        self.logger.info('worker msg is {0}{1}'.format(type(kwargs['msg']), kwargs['msg']))
        
        self.switch_off()

        try:
            self.register_health(health = kwargs['msg']) 
        except Exception as e:
            self.logger.error('Exception: {0}'.format(e))

        self.switch_on()
        return