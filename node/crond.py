#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: crond.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/07/05 21:28

import os
import asyncio
from .template import Template

class Crond(Template):
    def __init__(self, **kwargs):
        super(Crond, self).__init__(**kwargs)

        self.local_crond_file = os.path.join(self.exec_path, 'service.cron')
        return

    def generate_crond(self, **kwargs):
        #self.logger.debug('remote crond is {0}'.format(kwargs['remote_crond']))
        # clean local crond file
        with open(self.local_crond_file, 'w') as file_handler:
            for crond in kwargs['remote_crond']:
                if crond['type'] == 'script':
                    #self.logger.debug('value is {0}, path is {1}'.format(crond['value'], self.cron_path))
                    self.http_handler.download(url = crond['value'], target_path = self.cron_path)
                    local_crond_script = os.path.join(self.cron_path, os.path.basename(crond['value']))
                    self.shell_handler.exec_cmd(cmd = 'chmod +x {0}'.format(local_crond_script), timeout = 1)
                    file_handler.write('{0} {1}\n'.format(crond['crond'], local_crond_script))
                else:
                    file_handler.write('{0} {1}\n'.format(crond['crond'], crond['value']))
        
        # crontab -e
        self.shell_handler.exec_cmd(cmd = 'crontab {0}'.format(self.local_crond_file), timeout = 1)
        return

    # reload
    async def whisper(self, **kwargs):
        while True:
            self.logger.debug('this is {0} whisper.'.format(self.name))
            if not self.init:
                self.logger.debug('self init is {0}'.format(self.init))
                self.generate_crond(remote_crond = self.kv_handler.get_json(key = self.kv_key))
                self.init = True
            await asyncio.sleep(5)
        return
    
    # reload
    def worker(self, **kwargs):
        self.logger.info('worker msg is {0}{1}'.format(type(kwargs['msg']), kwargs['msg']))
        
        self.switch_off()

        try:
            self.generate_crond(remote_crond = kwargs['msg'])
        except Exception as e:
            self.logger.error('Exception: {0}'.format(e))

        self.switch_on()
        return