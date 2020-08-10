#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: Configure.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/06/28 21:28

import os
import asyncio
from .template import Template

class Configure(Template):
    def __init__(self, **kwargs):
        super(Configure, self).__init__(**kwargs)

        self.local_yaml_file = os.path.join(self.exec_path, 'service.yaml')
        self.local_conf_file = os.path.join(self.exec_path, 'service.conf')
        return

    def save_config(self, **kwargs):
        # save yaml
        self.file_handler.dumps(file = self.local_yaml_file, content = kwargs['config'], type = 'yaml')

        # save conf
        with open(self.local_conf_file, 'w') as file_handler:
            for section in kwargs['config'].keys():
                #self.logger.debug('section is {0}'.format(section))
                file_handler.write('[{0}]\n'.format(section))
                for key in kwargs['config'][section].keys():
                    #self.logger.debug('key is {0}'.format(key))
                    file_handler.write('{0} = {1}\n'.format(key, kwargs['config'][section][key]))
        return

    def generate_config(self, **kwargs):
        local_conf = self.file_handler.loads(file = self.local_yaml_file, type = 'yaml')
        self.logger.debug('local config is {0}, remote config is {1}'.format(local_conf, kwargs['remote_conf']))
        if local_conf == kwargs['remote_conf']:
            self.logger.info('config not need re-generate.')
        else:
            self.logger.info('config need re-generate')
            self.save_config(config = kwargs['remote_conf'])
            self.exec_hook(hook_name = 'restart')
        return

    # reload
    async def whisper(self, **kwargs):
        while True:
            self.logger.debug('this is {0} whisper.'.format(self.name))
            if not self.init:
                self.logger.debug('self init is {0}'.format(self.init))
                self.generate_config(remote_conf = self.kv_handler.get_json(key = self.kv_key))
                self.init = True
            await asyncio.sleep(5)
        return
    
    # reload
    def worker(self, **kwargs):
        self.logger.info('worker msg is {0}{1}'.format(type(kwargs['msg']), kwargs['msg']))
        
        self.switch_off()

        try:
            self.generate_config(remote_conf = kwargs['msg']) 
        except Exception as e:
            self.logger.error('Exception: {0}'.format(e))

        self.switch_on()
        return