#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: commLog.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/2 10:28

import copy
import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler

class LogHandler(object):
    def __init__(self, configs):
        self.configs = configs
        self.log_level = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARN': logging.WARNING,
            'ERROR': logging.ERROR,
        }
        return

    def register_default(self, log_file):
        configs = copy.deepcopy(self.configs)
        configs['handlers']['default']['filename'] = \
            configs['handlers']['default']['filename'].replace('FILE', log_file)
        logging.config.dictConfig(configs)
        logger = logging.getLogger('default')
        return logger

    def register_rotate(self, log_file):
        log_level = self.log_level[self.configs['handlers']['default']['level'].upper()]
        log_format = logging.Formatter(self.configs['formatters']['default']['format'])
        log_file_name = self.configs['handlers']['default']['filename'].replace('FILE', log_file)
        handler = TimedRotatingFileHandler(
            log_file_name,
            when = 'midnight'
        )
        handler.setFormatter(log_format)
        self.logger = logging.getLogger(log_file_name)
        self.logger.addHandler(handler)
        self.logger.setLevel(log_level)
        return self.logger

##########################
'''
import logging
from logging.handlers import RotatingFileHandler

class LogHandler(object):
    def __init__(self, logfile, level):
        self.log_level = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARN': logging.WARNING,
            'ERROR': logging.ERROR,
        }
        self.filename = logfile
        self.level = self.log_level[level.upper()]
        self.format = logging.Formatter('[%(asctime)s] [%(process)d] [%(thread)d] [%(filename)20s] [line:%(lineno)4d] [%(levelname)-6s] %(message)s')
        self.logger = None
        return

    def register(self):
        handler = RotatingFileHandler(self.filename, maxBytes = 200*1024*1024, backupCount = 20)
        handler.setFormatter(self.format)
        self.logger = logging.getLogger(self.filename)
        self.logger.addHandler(handler)
        self.logger.setLevel(self.level)
        return self.logger

def get_logger(logfile, level):
    common_log = CommonLog(logfile, level)
    return common_log.register()
'''
'''
例子
'''

import sys
import time
if __name__ == '__main__':
    # init log
    log_file = './test.log'
    log_level = 'DEBUG'
    LOG = get_logger(log_file, log_level)

    while True:
        LOG.debug('this is debug log')
        LOG.info('this is info log')
        LOG.error('this is error log')
        time.sleep(0.01)
    sys.exit(0)