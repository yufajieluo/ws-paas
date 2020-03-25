#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: node.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/2 10:28

import time

class TimerHandler(object):
    def __init__(self):
        self.timers = []
        return
    def add_timer(self, timer):
        if timer in self.timers:
            return
        self.timers.append(timer)

    def del_timer(self, timer):
        if timer in self.timers:
            self.timers.remove(timer)
        return

    def start_timer(self):
        for timer in self.timers:
            timer.start_timer()
    def deamon_loop(self):
        self.start_timer()
        while True:
            for timer in self.timers:
                try:
                    timer.count_timer()
                except Exception as e:
                    print ('unknown error(%s) when process timer %s' % (e,timer.process))
                    continue
            time.sleep(1)
        return

class Timer(object):
    def __init__(self, interval, process, parameters = None, delay_second = 0):
        self.interval = interval
        self.process = process
        self.parameters = parameters
        self.tmp = delay_second
        self.start = 0
        return

    def start_timer(self):
        self.start = time.time()
        return

    def count_timer(self):
        now = time.time()
        elapse = now - self.start
        self.start = now
        if elapse > 0:
            self.tmp -= elapse
            if self.tmp < 0:
                return self.run()
        if time.time() - self.start >= self.interval:
            return self.start_timer()

    def run(self):
        self.tmp = self.interval
        return self.process(self.parameters)