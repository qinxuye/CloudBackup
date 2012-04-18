#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-4-18

@author: Chine
'''

import urllib, urllib2
import json
import time

from errors import VdiskError
from utils import hmac_sha256

__author__ = "Chine King"
__description__ = "A client for vdisk api, site: http://vdisk.me/api/doc"

endpoint = "http://openapi.vdisk.me/"

def _call(url_params, params, headers=None, method="POST", try_times=3, try_interval=3):
    def _get_data():
        if method == "GET":
            full_params = "&".join((url_params, urllib.urlencode(params)))
            path = "%s?%s" %(endpoint, full_params)
            resp = urllib2.urlopen(path)
            return json.loads(resp.read())
        
        # if method is POST
        path = "%s?%s" % (endpoint, url_params)
        encoded_params = urllib.urlencode(params)
        
        if headers is not None:
            req = urllib2.Request(path, encoded_params, headers)
            resp = urllib2.urlopen(req)
        else:
            resp = urllib2.urlopen(path, encoded_params)
            
        return json.loads(resp.read())
    
    for i in range(try_times):
        try:
            return _get_data()
        except urllib2.HTTPError:
            time.sleep(try_interval)
            
        raise VdiskError(-1, "Can't not connect to server")

def get_signature(data, app_secret):
    data_str = '&'.join(['%s=%s' % (k, data[k]) for k in sorted(data)])
    return hmac_sha256(app_secret, data_str)

class VdiskClient(object):
    def __init__(self, app_key, app_secret):
        self.app_key = app_key
        self.app_secret = app_secret
    
    def get_token(self, account, password, app_type="local"):
        params = {
                  'account': account,
                  'password': password,
                  'appkey': self.app_key,
                  'time': time.time()
                  }
        params['signature'] = get_signature(params, self.app_secret)
        if app_type != 'local':
            params['app_type'] = app_type
            
        result = _call('m=auth&a=get_token', params)
        if result['err_code'] != 0:
            raise VdiskError(result['err_code'], result['err_msg'])
        
        return result['data']

    