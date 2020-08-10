#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: commInstance.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/05/14 20:28

import socket
from .commHttp import HttpHandler

class InstanceHandler(object):
    def __init__(self):
        self.http_handler = HttpHandler(None, None)
        return
    
    def get_public_addr(self, **kwargs):
        try:
            result = self.http_handler.get(url = kwargs['url'], data = None)
            addr = result if result else ''
        except Exception as e:
            addr = ''
        return addr
    
    def get_private_addr(self):
        try:
            addrs = socket.getaddrinfo(socket.gethostname(), None)
            addr = [item[4][0] for item in addrs if ':' not in item[4][0]][0]
        except Exception as e:
            addr = ''
        return addr



if __name__ == '__main__':
    instance_handler = InstanceHandler()
    print(instance_handler.get_public_addr(url = 'http://wgetip.com'))
    print('===')
    print(instance_handler.get_private_addr())