#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-4-18

@author: Chine
'''

import urllib, urllib2
import json
import time
import os

from errors import VdiskError
from utils import hmac_sha256, encode_multipart

__author__ = "Chine King"
__description__ = "A client for vdisk api, site: http://vdisk.me/api/doc"

endpoint = "http://openapi.vdisk.me/"

def _call(url_params, params, headers=None, method="POST", try_times=3, try_interval=3):
    def _get_data():
        if method == "GET":
            if isinstance(params, str):
                full_params = "&".join((url_params, params))
            else:
                full_params = "&".join((url_params, urllib.urlencode(params)))
            path = "%s?%s" %(endpoint, full_params)
            resp = urllib2.urlopen(path)
            return json.loads(resp.read())
        
        # if method is POST
        path = "%s?%s" % (endpoint, url_params)
        if isinstance(params, str):
            encoded_params = params
        else:
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
        self.dologid = 0
    
    def auth(self, account, password, app_type="local"):
        self.account, self.password = account, password
        self.token = self.get_token(account, password, app_type)
        self._base_oper('a=keep', {'token': self.token}) # init dologid
        
    def _base_oper(self, url_params, params, **kwargs):
        result = _call(url_params, params, **kwargs)
        
        if result['err_code'] != 0:
            raise VdiskError(result['err_code'], result['err_msg'])
        
        self.dologid = result['dologid']
        
        return result.get('data'), result['dologdir']
    
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
        
        return result['data']['token']
    
    def keep(self):
        self._base_oper('a=keep', {'token': self.token, 
                                   'dologid': self.dologid})
                                                  
    def keep_token(self):
        return self._base_oper('m=user&a=keep_token', {'token': self.token, 
                                                       'dologid': self.dologid})
        
    def upload_file(self, filename, dir_id, cover, maxsize=10, callback=None, dir=None):
        try:
            if os.path.getsize(filename) > maxsize * (1024 ** 2):
                raise VdiskError(-1, 'The file is larger than %dM' % maxsize)
        except os.error:
            raise VdiskError(-1, 'Can\'t access the file')
        
        fp = open(filename, 'rb')
        try:
            params = {
                      'token': self.token,
                      'dir_id': dir_id,
                      'cover': 'yes' if cover else 'no',
                      'file': fp,
                      'dologid': self.dologid
                      }
            
            if callback:
                params['callback'] = callback
            if dir:
                params['dir'] = dir
        
            
            params, boundary = encode_multipart(params)
            
            headers = {
                       'Content-Type': 'multipart/form-data; boundary=%s' % boundary
                       }
            
            return self._base_oper('m=file&a=upload_file', params, headers=headers)
        finally:
            fp.close()