#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: wshttp.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/2 10:28

import tornado.web
import tornado.ioloop

class HttpApp(object):
    def __init__(self, logger, configs):
        self.app = None
        self.port = configs['default']['http_port']
        self.logger = logger
        return
    
    def make_app(self):
        self.app = tornado.web.Application(
            [
                (r'/', MainHandler, {'logger': self.logger}),
            ]
        )
    
    def process(self, **kwargs):
        self.make_app()
        self.app.listen(self.port)
        tornado.ioloop.IOLoop.current().start()


class MainHandler(tornado.web.RequestHandler):
    def initialize(self, logger):
        self.logger = logger
        return

    def get(self):
        self.logger.debug('http get')
        self.write({'echo': 'node agent.'})