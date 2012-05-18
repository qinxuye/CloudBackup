#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-5-1

@author: Chine
'''

__author__ = "Chine King"

import os
import sys

def join_path(*path):
    return '/'.join([p.strip('/') for p in path])

def join_local_path(*path):
    return os.path.join(*(p.replace('/', os.sep) for p in path))

def get_sys_encoding():
    return sys.getfilesystemencoding()