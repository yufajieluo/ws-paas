#!/usr/bin/python
#-*-coding:utf-8-*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# copyright 2020 WShuai, Inc.
# All Rights Reserved.

# @File: item_template.py
# @Author: WShuai, WShuai, Inc.
# @Time: 2020/3/2 10:28

import sys
import argparse
from node import node

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", help="type",type=str, choices=['center', 'node'], required=True)
    args = parser.parse_args()

    if args.type == 'center':
        pass
    elif args.type == 'node':
        config_file = 'config/{0}.yaml'.format(args.type)
        node_handler = node.Node(config_file)
        node_handler.start()
    sys.exit(0)