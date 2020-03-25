#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: commShell.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/13 10:28

import time
import subprocess

class ShellHandler(object):
    def __init__(self):
        return
    
    def exec_cmd(self, **kwargs):
        ret_code = None
        ret_out = None
        ret_err = None

        if kwargs['specific_user']:
            cmd = 'su - {0} -c \'{1}\''.format(kwargs['specific_user'], cmd)
        
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
                    sp_out = None
                    sp_re = 'System CMD Timeout'
                    break
                else:
                    time.sleep(0.1)
                    continue
        return code, out, err