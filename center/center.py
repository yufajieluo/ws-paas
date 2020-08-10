#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: center.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/07/09 10:28

import os
import sys
import time
sys.path.append(os.path.dirname(__file__) + os.sep + '../')
import multiprocessing

from common import commMonkey
from common.commLog import LogHandler
from common.commFile import FileHandler
from common.commRedis import RedisHandler
from common.commQueue import QueueHandler
from common.commConsul import ConsulHandler

class Center(object):
    def __init__(self, config_file):
        self.config_file = config_file
        return

    def start(self):
        # init config with yaml
        file_handler = FileHandler()
        configs = file_handler.loads(file = self.config_file, type = 'yaml')
        print('read config is {0}'.format(configs))

        # init log
        logger_handler = LogHandler(configs['logging'])
        logger = logger_handler.register_rotate(self.__class__.__name__.lower())
        #logger = logger_handler.register_default(self.__class__.__name__.lower())
        logger.info('service configs is {0}'.format(configs))

        configs['handler'] = {}

        # init KV
        if configs['default']['kv_system'] == 'consul':
            kv_handler = ConsulHandler(configs['kv']['host'], configs['kv']['port'])
            kv_handler.connect()
        elif configs['default']['kv_system'] == 'etcd':
            pass
        else:
            pass
        configs['handler']['kv'] = kv_handler

        # init redis
        interval = 0
        redis_handler = RedisHandler(
            host = configs['redis']['host'],
            port = configs['redis']['port'],
            pswd = configs['redis']['pswd'],
            db = configs['redis']['db']
        )
        while True:
            if redis_handler.connect():
                logger.info('connect to redis success.')
                break
            else:
                interval += 1
                logger.error('connect to redis failed, retry {0}s later.'.format(interval % 10))
                time.sleep(interval % 10)
                continue
        configs['handler']['redis'] = redis_handler
        
        # init manager
        multiprocessing.managers.AutoProxy = commMonkey.AutoProxy
        manager = multiprocessing.Manager()
        lock = manager.Lock()
        shm = manager.dict(configs['shm'])
        queue = QueueHandler(
            generic = manager,
            maxsize = configs['queue']['size'],
            timeout = configs['queue']['timeout']
        )

        process_pros = []
        for process in configs['processes']:     
            import_str = None
            for root, dirs, files in os.walk(os.path.dirname(__file__)):
                if '{0}.py'.format(process['file']) in files:
                    import_str = '{0}.{1}'.format(self.__class__.__name__.lower(), process['file'])
                    break

            if not import_str:
                logger.error('process config {0} matched class file not found.'.format(process['name']))
                continue
            else:
                #process_logger = logger_handler.register_rotate(process['name'])
                process_logger = logger_handler.register_default(process['name'])
                exec('import {0}'.format(import_str))
                logger.debug('{0}.{1}.{2}(process_logger, configs, shm, lock, queue, dependent)'.format(
                        self.__class__.__name__.lower(),
                        process['file'], 
                        process['class'],
                    )
                )
                
                dependent = process['dependent']
                process_obj = eval(
                    '{0}.{1}.{2}(\
                        logger = process_logger, \
                        configs = configs, \
                        shm = shm, \
                        lock = lock, \
                        queue = queue, \
                        dependent = dependent \
                    )'.format(
                        self.__class__.__name__.lower(),
                        process['file'], 
                        process['class'],
                    )
                )
                process_obj.start()
                process_pros.append(process_obj)
            
        while True:
            logger.debug('this is center main process {} ...'.format(os.getpid()))
            logger.debug('shm is {0}'.format(shm))

            if not shm['running']:
                for process_pro in process_pros:
                    process_pro.terminate()
                logger.info('man process exit.')
                break
            time.sleep(10)
        return