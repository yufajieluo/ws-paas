#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: commMonkey.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/10 10:28

import multiprocessing.managers

def AutoProxy(token, serializer, manager=None, authkey=None,
              exposed=None, incref=True, manager_owned=False):
    '''
    Return an auto-proxy for `token`
    '''
    _Client = multiprocessing.managers.listener_client[serializer][1]

    if exposed is None:
        conn = _Client(token.address, authkey=authkey)
        try:
            exposed = dispatch(conn, None, 'get_methods', (token,))
        finally:
            conn.close()

    if authkey is None and manager is not None:
        authkey = manager._authkey
    if authkey is None:
        authkey = multiprocessing.process.current_process().authkey

    ProxyType = multiprocessing.managers.MakeProxyType('AutoProxy[%s]' % token.typeid, exposed)
    proxy = ProxyType(token, serializer, manager=manager, authkey=authkey,
                      incref=incref, manager_owned=manager_owned)
    proxy._isauto = True
    return proxy