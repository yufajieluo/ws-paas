#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: commShell.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/13 10:28

import os
import time
import subprocess

class ShellHandler(object):
    def __init__(self):
        return
    
    def exec_cmd(self, **kwargs):
        ret_code = None
        ret_out = None
        ret_err = None

        if 'specific_user' in kwargs.keys() and kwargs['specific_user']:
            cmd = 'su - {0} -c \'{1}\''.format(kwargs['specific_user'], kwargs['cmd'])
        else:
            cmd = kwargs['cmd']

        sp = subprocess.Popen(cmd, shell = True, preexec_fn = os.setsid, close_fds = True)
        begin_time = time.time()
        seconds_passed = 0
        while True:
            if sp.poll() is not None:
                sp_ret = sp.communicate()
                ret_code = sp.poll() if sp.poll() else 0
                ret_out = sp_ret[0]
                ret_err = sp_ret[1]
                break
            else:
                if kwargs['timeout'] and time.time() - begin_time > kwargs['timeout']:
                    sp.terminate()
                    ret_code = 128
                    ret_out = 'System CMD Timeout'
                    ret_err = 'System CMD Timeout'
                    break
                else:
                    time.sleep(0.1)
                    continue
        return True if ret_code == 0 else False, ret_out, ret_err
    
if __name__ == '__main__':
    shell_handler = ShellHandler()
    cmd = '/data/before.sh'
    timeout = 11
    specific_user = 'root'
    code, out, err = shell_handler.exec_cmd(cmd = cmd, timeout = timeout, specific_user = specific_user)
    print('code is {0}, out is {1}, err is {2}'.format(code, out, err))