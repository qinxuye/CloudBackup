#!/usr/bin/env python
#coding=utf-8
'''
Copyright (c) 2012 chine <qin@qinxuye.me>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Created on 2012-5-1

@author: Chine
'''

__author__ = "Chine King"

import os
import sys
import platform
import subprocess

from CloudBackup.test.settings import EXE_COMPILE

def join_path(*path):
    return '/'.join([p.strip('/') for p in path])

def join_local_path(*path):
    return os.path.join(*(p.replace('/', os.sep) for p in path))

def get_sys_encoding():
    return sys.getfilesystemencoding()

def is_windows():
    return platform.system() is 'Windows'

def win_hide_file(log_file):
    if is_windows() and os.path.exists(log_file):
        subprocess.call('attrib +h %s' % log_file, shell=True)
        
get_root_path = lambda: os.path.dirname(__file__)

def get_info_path():
    if is_windows() and EXE_COMPILE:
        import win32api
        exe_name = win32api.GetModuleFileName((win32api.GetModuleHandle(None)))
        dirname = os.path.dirname(exe_name)
        
        return os.path.join(dirname, '.info')
    else:
        return os.path.join(get_root_path(), '.info')

def ensure_folder_exsits(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)