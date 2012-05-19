#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-5-19

@author: Chine
'''

import os
import time
import platform
import subprocess

class Log(object):
    def __init__(self, log_file):
        dirname = os.path.dirname(log_file)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        
        self.log_file = log_file
            
    def _win_hide(self):
        sys_name = platform.system()
        if sys_name == 'Windows' and os.path.exists(self.log_file):
            subprocess.call('attrib +h %s' % self.log_file, shell=True)
        
    def write(self, itm):
        fp = open(self.log_file, 'a+')
        try:
            time_str = time.strftime("%Y-%m-%d %X", time.localtime())
            content = '%s %s\n' % (time_str, itm)
            fp.write(content)
            self._win_hide()
        finally:
            fp.close()
            
    def write_logs(self, itms):
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
        fp = open(self.log_file)
        for itm in reversed(fp.readlines()):
            content = itm.strip()
            if len(content) > 0:
                yield content