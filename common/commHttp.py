#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: commHttp.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/05/14 20:28

import os
import requests

class HttpHandler(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        return

    def get(self, **kwargs):
        if len(kwargs['url']) and kwargs['url'][:4] == 'http':
            request_url = kwargs['url']
        else:
            request_url = os.path.join('http://{0}:{1}'.format(self.host, self.port), url)

        try:
            result = requests.get(request_url, data = kwargs['data'], timeout = 10)
            if result.status_code != 200:
                data = False
            else:
                data = result.text
        except Exception as e:
            data = False
        return data

    def download(self, **kwargs):
        if len(kwargs['url']) and kwargs['url'][:4] == 'http':
            request_url = kwargs['url']
        else:
            request_url = os.path.join('http://{0}:{1}'.format(self.host, self.port), url)

        resp = requests.get(request_url, stream = True)
        local_file = os.path.join(kwargs['target_path'], os.path.basename(request_url))
        with open(local_file, 'wb') as file_handler:
            for chunk in resp.iter_content(chunk_size = 51200):
                file_handler.write(chunk)

        return
    

if __name__ == '__main__':
    http_handler = HttpHandler(None, None)
    result = http_handler.get(url = 'http://wgetip.com', data = None)
    print('[{0}]'.format(result))

    result = http_handler.download(
        url = 'http://127.0.0.1:9000/public/agent-node.v2.0.1.tar.gz',
        target_path = '/tmp'
    )