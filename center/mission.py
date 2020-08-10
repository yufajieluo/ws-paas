#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: mission.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/07/19 19:38

import math
import time
import json

class Mission(object):
    def __init__(self, **kwargs):
        self.logger = None
        self.kv_handler = None
        self.redis_handler = None
        self.single_timeout = kwargs['single_timeout']
        self.kv_key_dc = kwargs['kv_key_dc']
        self.kv_key_dg = kwargs['kv_key_dg']
        self.redis_key = kwargs['redis_key']
        return
    
    def get_health_instances(self, **kwargs):
        health_instances = []
        try:
            _, nodes = self.kv_handler.get_health_nodes(service = kwargs['service'])
            for node in nodes:
                health = True
                for check in node['Checks']:
                    if check['Status'] == 'passing':
                        continue
                    else:
                        health = False
                        break
                if health:
                    health_instances.append(node['Service']['Address'])
        except Exception as e:
            self.logger.error('get {} health instances Exception: {}'.format(kwargs['service'], e))
        return health_instances

    def get_policy_num(self, **kwargs):
        if kwargs['type'] == 'num':
            num = kwargs['value'] if kwargs['value'] > 0 else 1
        elif kwargs['type'] == 'percent':
            num = int(math.ceil(kwargs['total'] * int(kwargs['value']) * 0.01)) if kwargs['value'] > 0 else 1
        else:
            num = 1
        return num

    def get_min_split(self, **kwargs):
        kv_key = self.kv_key_dg.replace(
            'DC_NAME', kwargs['dc_name']
        ).replace(
            'DG_NAME', kwargs['dg_name']
        ).replace(
            'KEY', 'policy'
        )
        policy = self.kv_handler.get_json(key = kv_key)
        try:
            once = self.get_policy_num(
                type = policy['once']['type'], 
                value = policy['once']['value'], 
                total = kwargs['total']
            )
            reserved = self.get_policy_num(
                type = policy['once']['type'], 
                value = policy['once']['value'], 
                total = kwargs['total']
            )

            self.logger.debug('total is {}, once is {}, reserved is {}'.format(kwargs['total'], once, reserved))
            
            if kwargs['total'] <= 1:
                min_split = 1
            elif kwargs['total'] - once >= reserved:
                min_split = once
            else:
                min_split = kwargs['total'] - reserved
        except Exception as e:
            self.logger.error('get min split Exception: {}'.format(e))
            min_split = int(math.ceil(float(kwargs['total']) / 10)) if kwargs['total'] > 0 else 1
        return min_split
    
    def get_next_split(self, **kwargs):
        return kwargs['all'][kwargs['min_split'] * kwargs['index'] : kwargs['min_split'] * (kwargs['index'] + 1)]

    def wait_split_resp(self, **kwargs):
        begin_time = time.time()
        while True:
            if time.time() - begin_time < self.single_timeout:
                if next_split:
                    for address in next_split:
                        response = self.redis_handler.conn.rpop(kwargs['res_key'].replace('INSTANCE', address))
                        if response['mission_id'] == kwargs['mission_id']:
                            if response['resp_status']:
                                kwargs['success'].append(address)
                            else:
                                kwargs['failed'].append(address)
                            next_split.remove(address)
                        elif response['mission_id'][:8] < kwargs['mission_id'][:8]:
                            pass # give up last day dirty resp
                        else:
                            self.redis_handler.conn.lpush(kwargs['res_key'].replace('INSTANCE', address), response)
                    time.sleep(1)
                else:
                    break
            else:
                kwargs['timeout'] += next_split
                break
        return success, failed, timeout


    def notify_redis(self, **kwargs):
        if kwargs['domain'] == 'dc':
            req_key = self.redis_key.replace(
                'TYPE', 'REQ'
            ).replace(
                'DC_NAME', kwargs['dc_name']
            ).replace(
                'KEY', kwargs['model']
            )

            res_key = self.redis_key.replace(
                'TYPE', 'RES'
            ).replace(
                'DC_NAME', kwargs['dc_name']
            ).replace(
                'KEY', kwargs['model']
            )
        else:
            req_key = self.redis_key.replace(
                'TYPE', 'REQ'
            ).replace(
                'DC_NAME', kwargs['dc_name']
            ).replace(
                'DG_NAME', kwargs['dg_name']
            ).replace(
                'KEY', kwargs['model']
            )

            res_key = self.redis_key.replace(
                'TYPE', 'RES'
            ).replace(
                'DC_NAME', kwargs['dc_name']
            ).replace(
                'DG_NAME', kwargs['dg_name']
            ).replace(
                'KEY', kwargs['model']
            )

        self.logger.debug('service is {}, req_key is {}, res key is {}'.format(kwargs['service'], req_key, res_key))
        
        success = []
        failed = []
        timeout = []
        instances = self.get_health_instances(service = kwargs['service'])
        self.logger.debug('instances is {}'.format(instances))

        min_split = self.get_min_split(dc_name = kwargs['dc_name'], dg_name = kwargs['dg_name'], total = len(instances))
        loop = int(math.ceil(float(len(instances)) / min_split))

        self.logger.debug('instances is {}, min_split is {}'.format(instances, min_split))
        for index in range(loop):
            next_split = self.get_next_split(all = instances, min_split = min_split, index = index)
            
            for address in next_split:
                self.redis_handler.conn.lpush(req_key.replace('INSTANCE', address), kwargs['value'])
            
            if kwargs['wait']:
                success, failed, timeout = self.wait_split_resp(
                    res_key = res_key, 
                    mission_id = kwargs['mission_id'], 
                    success = success,
                    failed = failed,
                    timeout = timeout
                )
            else:
                time.sleep(1)
        return

    def notify_kv(self, **kwargs):
        if kwargs['domain'] == 'dc':
            kv_key = self.kv_key_dc.replace(
                'DC_NAME', kwargs['dc_name']
            ).replace(
                'KEY', kwargs['model']
            )
        else:
            kv_key = self.kv_key_dg.replace(
                'DC_NAME', kwargs['dc_name']
            ).replace(
                'DG_NAME', kwargs['dg_name']
            ).replace(
                'KEY', kwargs['model']
            )

        self.kv_handler.put(key = kv_key, value = kwargs['value'])
        return
    
    def process_put(self, **kwargs):
        self.logger = kwargs['logger']
        self.kv_handler = kwargs['kv_handler']
        self.redis_handler = kwargs['redis_handler']
        self.logger.info('{} mission begin'.format(kwargs['msg']['mission_id']))

        value = json.dumps(kwargs['msg'][kwargs['domain']][kwargs['model']])
        dc_name = kwargs['msg']['dc']['info']['name']
        try:
            service = kwargs['msg']['dg']['info']['service']
            dg_name = kwargs['msg']['dg']['info']['name']
            
        except:
            service = None
            dg_name = None

        self.logger.info('{} mission value is {}'.format(kwargs['msg']['mission_id'], value))

        self.notify_kv(
            dc_name = dc_name,
            dg_name = dg_name,
            msg = kwargs['msg'],
            domain = kwargs['domain'],
            model = kwargs['model'],
            value = value
        )

        if kwargs['notify_redis']:
            self.notify_redis(
                mission_id = kwargs['msg']['mission_id'],
                service = service,
                dc_name = dc_name,
                dg_name = dg_name,
                msg = kwargs['msg'],
                domain = kwargs['domain'],
                model = kwargs['model'],
                value = value,
                wait = False
            )
        self.logger.info('{} mission finish'.format(kwargs['msg']['mission_id']))
        return