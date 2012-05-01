#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-5-1

@author: Chine
'''

__author__ = "Chine King"

def join_path(*path):
    return reduce(lambda p1, p2: '/'.join((p1.rstrip('/'), p2.lstrip('/'))), path)