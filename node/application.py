#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: application.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/9 10:28

import time
from queue import Empty, Full
from .template import Template

class Application(Template):
    def __init__(self, logger, configs):
        super(Application, self).__init__(logger, configs)
        self.kv_handler = configs['handler']['kv']
        
        return

    def process(self, **kwargs):        
        while True:
            self.logger.debug('this is application main process...')
            permit = self.permit(
                kwargs['shm']['status'][self.__class__.__name__.lower()]['intime'],
                kwargs['shm']['status'][self.__class__.__name__.lower()]['expect'],
            )
            if permit:
                try:
                    result = kwargs['shm']['queue'][self.__class__.__name__.lower()].get(timeout = 10)
                    self.logger.debug('get result from queue is {0}'.format(result))
                except Empty:
                    #self.logger.error('queue {0} is Empty'.format(self.__class__.__name__.lower()))
                    pass
                except Exception as e:
                    self.logger.error('Exception: {0}'.format(e))
            else:
                self.logger.info(
                    'status intime {0} and expect {1} not permit to process.'.format(
                        kwargs['shm']['status'][self.__class__.__name__.lower()]['intime'],
                        kwargs['shm']['status'][self.__class__.__name__.lower()]['expect'],
                    )
                )
                time.sleep(10)
        return