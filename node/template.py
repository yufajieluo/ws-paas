#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: template.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/9 10:28

import os
import pwd
import shutil
import hashlib
import requests
from ..common.commPress import PressHandler

class Template(object):
    def __init__(self, logger, configs):
        self.logger = logger
        self.config = configs
        self.name = None
        self.version = None
        self.intime_status = None
        self.expect_status = None
        if self.__class__.__name__.lower() in configs.keys():
            self.work_path = configs[self.__class__.__name__.lower()]['work_path']
            self.backup_path = configs[self.__class__.__name__.lower()]['back_path']

        self.key = None
        for key in configs['consul']['watchs']:
            if key['type'] == self.__class__.__name__.lower():
                self.key = key['key']
        return
    
    def permit(self, intime, expect):
        if intime == 'standby' and expect == 'normal':
            status = True
        elif intime == 'standby' and expect == 'fusing':
            status = False
        elif intime == 'active' and expect == 'normal':
            status = False
        elif intime == 'active' and expect == 'fusing':
            status = False
        else:
            status = False
        return status
    
    def download(self, **kwargs):
        resp = requests.get(kwargs['download_url'], stream = True)
        with open(kwargs['local_file'], 'wb') as file_handler:
            for chunk in resp.iter_content(chunk_size = 51200):
                file_handler.write(chunk)
        return
    
    def verify(self, **kwargs):
        md5 = None
        with open(kwargs['local_file']) as file_handler:
            md5 = hashlib.md5(file_handler.read()).hexdigest()
        return md5 == kwargs['md5']

    def unpack(self, **kwargs):
        result = False
        if os.path.isfile(kwargs['local_file']):
            if not os.path.isdir(kwargs['temp_path']):
                os.path.makedirs(kwargs['temp_path'])
            file_handler = tarfile.open(self.local_path_file)
            file_handler.extractall(path = self.temp_path)
            file_handler.close()
            result = True
        return result
    
    def backup(self, **kwargs):
        press_handler = PressHandler()
        result =  press_handler.commpress(
            target = self.work_path,
            tarfile = os.path.join(self.back_path, '{0}.{1}.tar.gz'.format(self.name, self.version))
        )
        return result
    
    def cleanup(self, **kwargs):
        if os.path.isdir(kwargs['target_path']) and kwargs['target_path'] != '/':
            shutil.rmtree(kwargs['target_path'])
            os.mkdir(kwargs['target_path'])
            result = True
        else:
            result = False
        return result

    def load(self, **kwargs):
        if os.path.isfile(kwargs['appspec_yaml_file']):
            yaml_handler = YamlHandler()
            appspec_info = yaml_handler.loads(appspec_yaml_file)
        else:
            self.logger.error('app spec yaml file {0} not found.'.format(kwargs['appspec_yaml_file']))
        return appspec_info

    def setup(self, **kwargs):        
        # setup dirs
        shutil.copytree(kwargs['source_path'], kwargs['target_path'])

        # setup special files
        for movement in kwargs['appspec_info']['app']['movements']:
            if os.path.isfile(os.path.join(kwargs['source_path'], movement['source'])) and \
                os.path.isdir(movement['destination']):
                shutil.copy(movement['source'], movement['destination'])

        # chmod and chown
        for permission in kwargs['appspec_info']['app']['permissions']:
            try:
                if permission['mode']:
                    os.chmod(
                        permission['object'], 
                        eval('0o{0}'.format(permission['mode']))
                    )
                if permission['onwer'] and permission['group']:
                    os.chown(
                        permission['object'], 
                        pwd.getpwnam(permission['onwer']).pw_uid,
                        pwd.getpwnam(permission['onwer']).pw_gid
                    )
            except Exception as e:
                self.logger.error('permission object {0} Exception: {1}'.format(permission['object'], e))
        return

    def hook(self, **kwargs):
        for hook in kwargs['appspec_info']['hooks']:
            
        return