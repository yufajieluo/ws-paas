#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: template.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/9 10:28

import os
import sys
import pwd
import json
import shutil
import tarfile
import hashlib
import asyncio
sys.path.append(os.path.dirname(__file__) + os.sep + '../')
from common.commFile import FileHandler
from common.commHttp import HttpHandler
from common.commPress import PressHandler
from common.commShell import ShellHandler
from common.commInstance import InstanceHandler

class Template(object):
    def __init__(self, **kwargs):
        self.logger = kwargs['logger']
        self.config = kwargs['configs']
        self.shm = kwargs['shm']
        self.lock = kwargs['lock']
        self.dependent = kwargs['dependent']

        self.name = self.__class__.__name__.lower()
        self.md5 = None
        self.appname = None
        self.version = None
        self.port = None
        self.download_url = None
        self.init = None
        self.rollback = None
        self.appspec_info = {}
        self.http_handler = HttpHandler(None, None)
        self.file_handler = FileHandler()
        self.shell_handler = ShellHandler()
        self.press_handler = PressHandler()

        # waiting for reload
        self.switcher = []

        self.kv_key = self.config['kv']['key'].replace(
            'DC_NAME', self.config['default']['dc_name']).replace(
            'DG_NAME', self.config['default']['dg_name']).replace(
            'KEY', self.name
        )
        self.watch_key = self.config['redis']['watch'].replace(
            'DC_NAME', self.config['default']['dc_name']).replace(
            'DG_NAME', self.config['default']['dg_name']).replace(
            'KEY', self.name
        )
        self.kv_handler = self.config['handler']['kv']
        self.redis_handler = self.config['handler']['redis']

        if self.name in self.config.keys():
            self.work_path = self.config[self.name]['work_path']
            self.back_path = self.config[self.name]['back_path']
            self.down_path = self.config[self.name]['down_path']
            self.temp_path = self.config[self.name]['temp_path']
            self.cron_path = self.config[self.name]['cron_path']
            self.exec_path = self.config[self.name]['exec_path']
            self.pickle_file = self.config[self.name]['pickle_file']
            self.serializes = [
                {'type': 'pickle', 'file': self.config[self.name]['pickle_file']},
                {'type': 'yaml',   'file': os.path.join(self.work_path, 'appspec.yaml')}
            ]
        
        if self.dependent:
            self.work_path = self.config[self.dependent]['work_path']
            self.back_path = self.config[self.dependent]['back_path']
            self.down_path = self.config[self.dependent]['down_path']
            self.temp_path = self.config[self.dependent]['temp_path']
            self.cron_path = self.config[self.dependent]['cron_path']
            self.exec_path = self.config[self.dependent]['exec_path']
            self.pickle_file = self.config[self.dependent]['pickle_file']
        
        if not os.path.isdir(self.work_path):
            os.makedirs(self.work_path)
        if not os.path.isdir(self.back_path):
            os.makedirs(self.back_path)
        if not os.path.isdir(self.down_path):
            os.makedirs(self.down_path)
        if not os.path.isdir(self.temp_path):
            os.makedirs(self.temp_path)
        if not os.path.isdir(self.cron_path):
            os.makedirs(self.cron_path)
        if not os.path.isdir(os.path.dirname(self.pickle_file)):
            os.makedirs(os.path.dirname(self.pickle_file))
        
        instance_handler = InstanceHandler()
        self.public_addr = instance_handler.get_public_addr(url = self.config['default']['dyndns_url'])
        self.private_addr = instance_handler.get_private_addr()
        return
    
    def get_local_version(self, **kwargs):
        local_version = None
        local_md5 = None
        local_download_url = None

        file_handler = FileHandler()
        for serialize in self.serializes:
            serialize_info = file_handler.loads(file = serialize['file'], type = serialize['type'])
            try:
                if self.appname:
                    if self.appname == serialize_info['app']['name']:
                        local_version = serialize_info['app']['version']
                        if 'md5' in serialize_info['app'].keys():
                            local_md5 = serialize_info['app']['md5']
                        if 'download_url' in serialize_info['app'].keys():
                            local_download_url = serialize_info['app']['download_url']
                        break
                else:
                    self.appname = serialize_info['app']['name']
                    local_version = serialize_info['app']['version']
                    if 'md5' in serialize_info['app'].keys():
                        local_md5 = serialize_info['app']['md5']
                    if 'download_url' in serialize_info['app'].keys():
                        local_download_url = serialize_info['app']['download_url']
                    break
            except Exception as e:
                self.logger.error('loads info Exception: {0}'.format(e))
                continue
        return local_version, local_md5, local_download_url
    
    def get_remote_version(self, **kwargs):
        try:
            value = self.kv_handler.get_json(key = self.kv_key)
            remote_version = value['version']
            remote_md5 = value['md5']
            remote_download_url = value['download_url']
        except Exception as e:
            remote_version = None
            remote_md5 = None
            remote_download_url = None
            self.logger.error('get remote version Exception: {0}'.format(e))
        return remote_version, remote_md5, remote_download_url
    
    def get_current_version(self, **kwargs):
        local_version, local_md5, local_download_url = self.get_local_version()
        remote_version, remote_md5, remote_download_url = self.get_remote_version()
        if remote_version == local_version:
            self.md5 = local_md5
            self.version = local_version
            self.download_url = local_download_url
        return

    def is_switch(self, **kwargs):
        return self.shm['status'][self.name]['intime'] == 'normal' and \
               self.shm['status'][self.name]['expect'] == 'normal'
        
    def switch_on(self, **kwargs):
        self.lock.acquire()
        shm_status = self.shm['status']
        shm_status[self.name]['intime'] = 'normal'
        self.shm['status'] = shm_status
        self.lock.release()
        return
    
    def switch_off(self, **kwargs):
        self.lock.acquire()
        shm_status = self.shm['status']
        shm_status[self.name]['intime'] = 'pending'
        self.shm['status'] = shm_status
        self.lock.release()
        return

    def levy(self, **kwargs):
        self.lock.acquire()
        shm_status = self.shm['status']

        for key in shm_status.keys():
            if key != self.name:
                shm_status[key]['expect'] = 'pending'
        
        self.shm['status'] = shm_status
        self.lock.release()
        return
    
    def is_levy(self, **kwargs):
        return self.shm['status'][self.name]['expect'] == 'pending'

    def disband(self, **kwargs):
        self.lock.acquire()
        shm_status = self.shm['status']

        for key in shm_status.keys():
            if key != self.name:
                shm_status[key]['intime'] = 'normal'
                shm_status[key]['expect'] = 'normal'
        
        self.shm['status'] = shm_status
        self.lock.release()
        return
    
    def enlist(self, **kwargs):
        self.lock.acquire()
        shm_status = self.shm['status']
        shm_status[self.name]['intime'] = 'ready'
        self.shm['status'] = shm_status
        self.lock.release()
        return

    def is_reunify(self, **kwargs):
        is_reunify = True
        for key in self.shm['status'].keys():
            if key != self.name:
                if self.shm['status'][key]['intime'] != 'ready':
                    is_reunify = False
                    break
        return is_reunify

    def shutdown(self, **kwargs):
        self.lock.acquire()
        self.shm['running'] = False
        self.lock.release()
        return
    
    def is_maintain(self, **kwargs):
        return self.shm['maintain']
    
    def set_maintain(self, **kwargs):
        self.lock.acquire()
        self.shm['maintain'] = kwargs['maintain']
        self.lock.release()
        return
    
    def recv(self, **kwargs):
        result = self.redis_handler.conn.rpop(self.watch_key)
        try:
            return json.loads(result)
        except Exception as e:
            #self.logger.error('recv from redis msg {0} is not loads to json.'.format(result))
            return None
    
    def download(self, **kwargs):
        self.http_handler.download(url = kwargs['download_url'], target_path = self.down_path)
        return True
    
    def verify(self, **kwargs):
        md5 = None
        local_file = os.path.join(self.down_path, os.path.basename(kwargs['download_url']))
        with open(local_file, 'rb') as file_handler:
            md5 = hashlib.md5(file_handler.read()).hexdigest()
        return md5 == kwargs['md5']

    def unpack(self, **kwargs):
        result = False
        local_file = os.path.join(self.down_path, os.path.basename(kwargs['download_url']))
        if os.path.isfile(local_file):
            try:
                self.cleanup(target_path = self.temp_path)
                result = self.press_handler.uncommpress(
                    target = self.temp_path,
                    tarfile = local_file
                )
            except Exception as e:
                self.logger.error('unpack file {0} to {1} Exception: {2}'.format(local_file, self.temp_path, e))
                result = False
        return result
    
    def cleanup(self, **kwargs):
        if os.path.isdir(kwargs['target_path']) and kwargs['target_path'] != '/':
            shutil.rmtree(kwargs['target_path'])
            os.mkdir(kwargs['target_path'])
            result = True
        else:
            result = False
        return result
    
    def backup(self, **kwargs):
        result = self.press_handler.commpress(
            target = self.work_path,
            tarfile = os.path.join(self.back_path, '{0}.{1}.tar.gz'.format(self.appname, self.version))
        )

        result = self.cleanup(target_path = self.work_path)
        return result
    
    def loadup(self, **kwargs):
        self.rollback = True

        appspec_yaml_file = os.path.join(self.temp_path, 'appspec.yaml')
        if os.path.isfile(appspec_yaml_file):
            self.appspec_info = self.file_handler.loads(file = appspec_yaml_file, type = 'yaml')
            result = True
        else:
            self.logger.error('app spec yaml file {0} not found.'.format(appspec_yaml_file))
            result = False
        return result

    def setup(self, **kwargs):
        # setup dirs
        for file in os.listdir(self.temp_path):
            source_file = os.path.join(self.temp_path, file)
            target_file = os.path.join(self.work_path, file)
            if os.path.isfile(source_file):
                shutil.copyfile(source_file, target_file)
            else:
                shutil.copytree(source_file, target_file)

        # setup special files
        for movement in self.appspec_info['app']['movements']:
            if movement:
                try:
                    if os.path.exists(os.path.join(self.temp_path, movement['source'])):
                        if not os.path.isdir(os.path.dirname(movement['destination'])):
                            os.makedirs(os.path.dirname(movement['destination']))
                        shutil.copy(os.path.join(self.temp_path, movement['source']), movement['destination'])
                        if movement['mode']:
                            self.shell_handler.exec_cmd(
                                cmd = 'chmod {0} {1}'.format(movement['mode'], movement['destination']),
                                timeout = 1
                            )
                except Exception as e:
                    self.logger.error('SETUP movement Exception: {0}'.format(e))

        # chmod and chown
        for permission in self.appspec_info['app']['permissions']:
            try:
                if permission['mode']:
                    #os.chmod(
                    #    os.path.join(self.work_path, permission['object']), 
                    #    eval('0o{0}'.format(permission['mode']))
                    #)
                    self.shell_handler.exec_cmd(
                        cmd = 'chmod {0} {1}'.format(
                            permission['mode'],
                            os.path.join(self.work_path, permission['object'])
                        ),
                        timeout = 1
                    )
                if permission['owner'] and permission['group']:
                    #os.chown(
                    #    os.path.join(self.work_path, permission['object']), 
                    #    pwd.getpwnam(permission['owner']).pw_uid,
                    #    pwd.getpwnam(permission['owner']).pw_gid
                    #)
                    self.shell_handler.exec_cmd(
                        cmd = 'chown -R {0}:{1} {2}'.format(
                            permission['owner'],
                            permission['group'],
                            os.path.join(self.work_path, permission['object'])
                        ),
                        timeout = 1
                    )
            except Exception as e:
                self.logger.error('permission object {0} Exception: {1}'.format(permission['object'], e))
        
        return True
    
    # upgrade hook
    def hookup(self, **kwargs):
        result = True
        #current_dir = os.getcwd()
        #current_dir = os.path.abspath(__file__)
        for hook in self.appspec_info['app']['hooks']:
            if hook['upgrade']:
                self.logger.info('exec hook {0} begin.'.format(hook['file']))
                os.chdir(os.path.dirname(os.path.join(self.work_path, hook['file'])))
                code, out, err = self.shell_handler.exec_cmd(
                    cmd = os.path.join(self.work_path, hook['file']),
                    specific_user = hook['role'],
                    timeout = hook['timeout']
                )
                if code:
                    self.logger.info('exec hook {0} success.'.format(hook['file']))
                    continue
                else:
                    self.logger.error('exec hook {0} failed, err is {1}.'.format(hook['file'], err))
                    result = False
                    break
        #os.chdir(current_dir)
        return result

    # normal hook
    def exec_hook(self, **kwargs):
        result = False
        # get current hook
        appspec_yaml_file = os.path.join(self.work_path, 'appspec.yaml')
        if os.path.isfile(appspec_yaml_file):
            appspec_info = self.file_handler.loads(file = appspec_yaml_file, type = 'yaml')
            for hook in appspec_info['app']['hooks']:
                if hook['name'] == kwargs['hook_name']:
                    self.shell_handler.exec_cmd(
                        cmd = os.path.join(self.work_path, hook['file']),
                        specific_user = hook['role'],
                        timeout = hook['timeout']
                    )
                    result = True
                    break
                else:
                    continue
        else:
            self.logger.error('app spec yaml file {0} not found.'.format(appspec_yaml_file))
            result = False
        return result
    
    def windup(self, **kwargs):
        self.cleanup(target_path = self.temp_path)
        self.rollback = False
        self.download_url = kwargs['download_url']
        self.md5 = kwargs['md5']
        self.version = kwargs['version']
        self.appname = kwargs['name']
        self.file_handler.dumps(
            type = 'pickle',
            file = self.pickle_file, 
            content = {
                'app': {
                    'name': self.appname, 
                    'version': self.version,
                    'md5': self.md5,
                    'download_url': self.download_url
                }
            }
        )
        local_package_file = os.path.join(self.down_path, os.path.basename(self.download_url))
        if os.path.isfile(local_package_file):
            os.remove(local_package_file)
        return True
    
    def register(self, **kwargs):
        try:
            self.port = self.appspec_info['app']['port']
        except Exception as e:
            self.port = 0
        
        self.kv_handler.register_service(
            name = self.appname,
            address = self.private_addr,
            port = self.port,
            tags = [
                'name:{0}'.format(self.appname),
                'port:{0}'.format(self.port),
                'version:{0}'.format(self.version),
                'lan:{0}'.format(self.private_addr),
                'wan:{0}'.format(self.public_addr)
            ]
        )
        return True
    
    def upgrade(self, **kwargs):
        result = True
        for case in self.switcher:
            self.logger.info('execute {0} begin.'.format(case['name']))
            if case['func'](**kwargs):
                self.logger.info('execute {0} success.'.format(case['name']))
                continue
            else:
                self.logger.error('execute {0} failed.'.format(case['name']))
                result = False
                break
        return result

    async def watcher(self, **kwargs):
        #self.logger.debug('this is watcher')
        while True:
            self.logger.debug('this is watcher')
            if self.is_levy():
                self.enlist()
                await asyncio.sleep(5)
            else:
                if self.is_switch():
                    msg = self.recv()
                    if msg:
                        self.worker(msg = msg)
                    else:
                        await asyncio.sleep(5)
                else:
                    await asyncio.sleep(5)
        return
    
    async def whisper(self, **kwargs):
        #self.logger.debug('this is whisper')
        while True:
            self.logger.debug('this is {0} whisper.'.format(self.name))
            self.logger.debug('shm status is {0}'.format(self.shm))
            self.get_current_version()
            if not self.version:
                self.init = True
                self.logger.info('start up with no version on {0}, init default version.'.format(self.name))
                value = self.kv_handler.get_json(key = self.kv_key)
                self.logger.debug('kv key is {0}, value is {1}'.format(self.kv_key, value))
                self.worker(msg = value)
            self.logger.info('service {0} current version is {1}'.format(self.appname, self.version))
            
            if self.version and self.appname:
                self.init = False
            await asyncio.sleep(5)
        return

    def process(self, **kwargs):
        loop = asyncio.get_event_loop()
        loop_tasks = []
        loop_tasks.append(loop.create_task(self.whisper()))
        loop_tasks.append(loop.create_task(self.watcher()))
        loop.run_until_complete(asyncio.wait(loop_tasks))
        return

    # waiting for reload
    def stopold(self, **kwargs):
        return

    # waiting for reload
    def worker(self, **kwargs):
        return
