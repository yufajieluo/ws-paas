#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: application.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/9 10:28

import os
from .template import Template

class Application(Template):
    def __init__(self, **kwargs):
        super(Application, self).__init__(**kwargs)
        
        # reload
        self.switcher = [
            { 'name': 'DOWNLOAD', 'func': self.download },
            { 'name': 'VERIFY',   'func': self.verify   },
            { 'name': 'UNPACK',   'func': self.unpack   },
            { 'name': 'STOPOLD',  'func': self.stopold  },
            { 'name': 'BACKUP',   'func': self.backup   },
            { 'name': 'LOADUP',   'func': self.loadup   },
            { 'name': 'SETUP',    'func': self.setup    },
            { 'name': 'HOOKUP',   'func': self.hookup   },
            { 'name': 'WINDUP',   'func': self.windup   },
            { 'name': 'REGISTER', 'func': self.register },
        ]
        return

    # reload
    def stopold(self, **kwargs):
        self.exec_hook(hook_name = 'stop')
        return True

    # reload
    def worker(self, **kwargs):
        self.logger.info('worker msg is {0}{1}'.format(type(kwargs['msg']), kwargs['msg']))
        
        self.switch_off()
        self.set_maintain(maintain = True)

        try:
            #self.logger.debug('self.appname is {0}, self.version is {1}, kwargs is {2}, '.format(self.appname, self.version, kwargs))
            if (not self.appname and not self.version) or \
                (self.appname == kwargs['msg']['name'] and self.version != kwargs['msg']['version']):
                result = self.upgrade(
                    md5 = kwargs['msg']['md5'],
                    version = kwargs['msg']['version'],
                    name = kwargs['msg']['name'],
                    download_url = kwargs['msg']['download_url'],
                )
                self.logger.debug('upgrade result is {0}, self.init is {1}'.format(result, self.init))

                if not result:
                    self.cleanup(target_path = self.temp_path)

                if self.rollback and not self.init:
                    self.logger.info('upgrade to version {0} failed, rollback to {1}'.format(kwargs['msg']['version'], self.version))
                    self.upgrade(
                        md5 = self.md5,
                        version = self.version,
                        name = self.appname,
                        download_url = self.download_url,
                    )
            else:
                pass
        except Exception as e:
            self.logger.error('Exception: {0}'.format(e))
            if self.init:
                self.cleanup(target_path = self.work_path)
            self.cleanup(target_path = self.temp_path)

        self.switch_on()
        self.set_maintain(maintain = False)
        return