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

Created on 2012-5-19

@author: Chine
'''

import os
import time

from utils import win_hide_file

class Log(object):
    def __init__(self, log_file, hide=True):
        self.log_file = log_file
        self.hide = hide
            
    def _win_hide(self):
        if self.hide:
            win_hide_file(self.log_file)
            
    def _ensure_folder_exsits(self):
        dirname = os.path.dirname(self.log_file)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        
    def write(self, itm):
        self._ensure_folder_exsits()
        
        fp = open(self.log_file, 'a+')
        try:
            time_str = time.strftime("%Y-%m-%d %X", time.localtime())
            content = '%s %s\n' % (time_str, itm)
            fp.write(content)
            self._win_hide()
        finally:
            fp.close()
            
    def write_logs(self, itms):
        self._ensure_folder_exsits()
        
        fp = open(self.log_file, 'a+')
        try:
            for itm in itms:
                time_str = time.strftime("%Y-%m-%d %X", time.localtime())
                content = '%s %s\n' % (time_str, itm)
                fp.write(content)
            self._win_hide()
        finally:
            fp.close()
    
    def get_logs(self):
        if not os.path.exists(self.log_file):
            yield
        
        fp = open(self.log_file)
        for itm in reversed(fp.readlines()):
            content = itm.strip()
            if len(content) > 0:
                yield content