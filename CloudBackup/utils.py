#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-5-1

@author: Chine
'''

__author__ = "Chine King"

def join_path(*path):
    return '/'.join([p.strip('/') for p in path])