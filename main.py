#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: main.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/2 10:28

import os
import sys
import argparse
from node import node
from center import center

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', help = 'name', type = str, required = True)
    parser.add_argument('--type', help = 'type', type = str, choices=['center', 'node'], required = True)
    parser.add_argument('--conf', help = 'config file path', type = str, required = True)
    args = parser.parse_args()

    if args.type == 'center':
        config_file = os.path.join(args.conf, '{0}.yaml'.format(args.type))
        if os.path.isfile(config_file):
            center_handler = center.Center(config_file)
            center_handler.start()
        else:
            print('config file {0} not found'.format(config_file))
    elif args.type == 'node':
        config_file = os.path.join(args.conf, '{0}.yaml'.format(args.type))
        if os.path.isfile(config_file):
            node_handler = node.Node(config_file)
            node_handler.start()
        else:
            print('config file {0} not found'.format(config_file))
    sys.exit(0)