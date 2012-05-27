#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-5-26

@author: Chine
'''

import time
from datetime import datetime, timedelta

from CloudBackup.lib.vdisk import (VdiskClient as Client, 
                                   CryptoVdiskClient as CryptoClient)
from CloudBackup.lib.errors import VdiskError

MAX_REQUEST_PER_MINUTE = 150
MAX_REQUEST_THRESHOLD = 10
SLEEP_INTERVAL = 10

class VdiskClient(Client):
    '''
    A vdisk client to get rid of the problem 900:
    only 150 requests in a minute.
    '''
    
    def __init__(self, app_key, app_secret):
        super(VdiskClient, self).__init__(app_key, app_secret)
        self.count = 0
        self.start = datetime.now()
        
    def _base_oper(self, url_params, params, **kwargs):
        end = datetime.now()
        delta = end - self.start
        
        if delta < timedelta(minutes=1):
            self.count += 1
            if self.count >= MAX_REQUEST_PER_MINUTE - MAX_REQUEST_THRESHOLD:
                time.sleep(60 - delta.seconds)
        else:
            self.start = end
            self.count = 0
        
        def _action():
            return super(VdiskClient, self)._base_oper(url_params, params, **kwargs)
        
        try:
            return _action()
        except VdiskError, e:
            if e.err_no == 900:
                time.sleep(SLEEP_INTERVAL)
                return _action()
            else:
                raise e
                
    
class CryptoVdiskClient(CryptoClient, Client):
    '''
    A crypto vdisk client to get rid of the problem 900:
    only 150 requests in a minute.
    '''