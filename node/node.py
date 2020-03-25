#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: node.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/2 10:28

import os
import sys
import time
sys.path.append(os.path.dirname(__file__) + os.sep + '../')
import multiprocessing

from common import commMonkey
from common.commLog import LogHandler
from common.commYaml import YamlHandler
from common.commConfig import ConfigHandler
from common.commConsul import ConsulHandler


class Node(object):
    def __init__(self, config_file):
        self.config_file = config_file
        return
    
    def start(self):
        # init config with yaml
        yaml_handler = YamlHandler()
        configs = yaml_handler.loads(self.config_file)
        print('read config is {0}'.format(configs))

        # init log
        logger_handler = LogHandler(configs['logging'])
        logger = logger_handler.register_rotate(self.__class__.__name__.lower())
        logger.info('service configs is {0}'.format(configs))

        # init KV
        if configs['default']['kv_system'] == 'consul':
            kv_handler = ConsulHandler(configs['consul']['host'], configs['consul']['port'])
            kv_handler.connect()
        elif configs['default']['kv_system'] == 'etcd':
            pass
        else:
            pass
        configs['handler'] = {}
        configs['handler']['kv'] = kv_handler
        configs['watch'] = {}
        configs['watch']['class'] = '{0}Watch'.format(configs['default']['kv_system'].capitalize())

        # init manager
        multiprocessing.managers.AutoProxy = commMonkey.AutoProxy
        manager = multiprocessing.Manager()
        lock = manager.Lock()
        shm = manager.dict(configs['shm'])
        shm['queue'] = {}

        process_pros = []
        for process in configs['processes']:     
            import_str = None       
            for root, dirs, files in os.walk(self.__class__.__name__.lower()):
                if '{0}.py'.format(process['file']) in files:
                    import_str = '{0}.{1}'.format(self.__class__.__name__.lower(), process['file'])
                    break

            if not import_str:
                logger.error('process config {0} matched class file not found.'.format(process['name']))
                continue
            else:
                if process['queue']:
                    lock.acquire()
                    shm_queue = shm['queue']
                    shm_queue[process['name']] = manager.Queue()
                    shm['queue'] = shm_queue
                    lock.release()
                process_logger = logger_handler.register_rotate(process['name'])
                exec('import {0}'.format(import_str))
                process_obj = eval(
                    '{0}.{1}.{2}(process_logger, configs)'.format(
                        self.__class__.__name__.lower(),
                        process['file'], 
                        process['class']
                    )
                )
                process_pro = multiprocessing.Process(
                    name = process['name'],
                    target = eval('process_obj.{0}'.format(process['func'])),
                    kwargs = {'shm': shm}
                )
                process_pro.start()
                process_pros.append(process_pro)

        while True:
            logger.debug('this is node main process...')
            logger.debug('shm is {0}'.format(shm))
            time.sleep(10)
        return

'''
if __name__ == '__main__':

    # init config
    config_file = '../node.config'
    config_handler = ConfigHandler(config_file)
    configs = config_handler.get_configs()
    print('read config is {0}'.format(configs))

    # init log
    logger_handler = LogHandler()
    logger = logger_handler.register()
    logger.info('service configs is {0}'.format(configs))

    # init agent
    agent = Agent(logger)

    # init http
    http_app = HttpApp()

    processes = []
    
    agent_process = multiprocessing.process(target = agent.process, name = 'agent', args = ())
    processes.append(agent_process)

    http_process = multiprocessing.Process(target = http_app.process, name = 'http', args = (8002))
    processes.append(http_process)

    #for process in processes:
    #    process.start()
    map(multiprocessing.Process.start, processes)

    sys.exit(0)
'''