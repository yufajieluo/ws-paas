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
    def __init__(self, **kwargs):
        super(Agent, self).__init__(**kwargs)

        # reload
        self.switcher = [
            { 'name': 'DOWNLOAD', 'func': self.download },
            { 'name': 'VERIFY',   'func': self.verify   },
            { 'name': 'UNPACK',   'func': self.unpack   },
            { 'name': 'BACKUP',   'func': self.backup   },
            { 'name': 'LOADUP',   'func': self.loadup   },
            { 'name': 'SETUP',    'func': self.setup    },
            { 'name': 'HOOKUP',   'func': self.hookup   },
            { 'name': 'WINDUP',   'func': self.windup   },
            { 'name': 'STOPOLD',  'func': self.stopold  },
        ]
        return

    # reload
    def stopold(self, **kwargs):
        self.logger.info('Agent restart now. See you later~~')
        self.shutdown()
        os._exit(0)
        return True

    # reload
    def worker(self, **kwargs):
        self.logger.info('worker msg is {0}'.format(kwargs['msg']))

        self.switch_off()
        
        if (not self.appname and not self.version) or \
                (self.appname == kwargs['msg']['name'] and self.version != kwargs['msg']['version']):
            self.levy()  
            while True:
                if not self.is_reunify():
                    self.logger.debug('shm status is {0}'.format(self.shm))
                    self.logger.info('not all other process be ready, waiting...')
                    time.sleep(5)
                    continue
                else:
                    self.logger.info('all other process be ready.')
                    break
            self.upgrade(
                md5 = kwargs['msg']['md5'],
                version = kwargs['msg']['version'],
                name = kwargs['msg']['name'],
                download_url = kwargs['msg']['download_url']
            )
        else:
            self.logger.info('self.version {0}, target version {1}, not need to upgrade.'.format(self.version, kwargs['msg']['version']))
            self.switch_on()
        return

    
