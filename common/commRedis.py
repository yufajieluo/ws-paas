#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: commRedis.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/4/12 10:28

import redis

class RedisHandler(object):
    def __init__(self, **kwargs):
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.pswd = kwargs['pswd']
        self.db = kwargs['db']
        self.conn = None
        return
    
    def connect(self):
        result = False
        try:
            self.conn = redis.Redis(
                host = self.host,
                port = self.port,
                password = self.pswd,
                db = self.db,
                decode_responses = True
            )
            self.conn.ping()
            result = True
        except Exception as e:
            print('connect to redis {0}:{1} failed: {2}'.format(self.host, self.port, e))
            result = False
        return result