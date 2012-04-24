#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-4-20

@author: Chine
'''

import base64
import hmac
import hashlib
import datetime
import urllib2
import time

from errors import S3Error
from utils import XML

__author__ = "Chine King"
__description__ = "A client for Amazon S3 api, site: http://aws.amazon.com/documentation/s3/"

ACTION_TYPES = ('PUT', 'GET', 'DELETE')
GMT_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

end_point = "http://s3.amazonaws.com"

class XAmzAcl(object):
    def __init__(self):
        for val in ('private', 'public-read', 'public-read-write', 
                    'authenticated-read', 'bucket-owner-read', 
                    'bucket-owner-full-control'):
            setattr(self, val.replace('-', '_'), val)
X_AMZ_ACL = XAmzAcl()

class S3Client(object):
    def __init__(self, access_key, secret_access_key):
        self.access_key = access_key
        self.secret_key = secret_access_key
        
    def _get_date_str(self):
        return datetime.datetime.utcnow().strftime(GMT_FORMAT)
        
    def _get_authorization(self, 
                           action, 
                           content_md5='',
                           content_type='',
                           date_str='',
                           canonicalized_amz_headers='',
                           canonicalized_resource=''):
        
        assert action in ACTION_TYPES # action must be put, get and delete
        
        date_set = True
        if not date_str:
            date_str = self._get_date_str()
            date_set = False

        string_to_sign = '%s\n%s\n%s\n%s\n%s%s' % (
                            action,
                            content_md5,
                            content_type,
                            date_str,
                            canonicalized_amz_headers,
                            canonicalized_resource
                         )
        print string_to_sign
        signature = base64.b64encode(
                        hmac.new(self.secret_key, string_to_sign, hashlib.sha1).digest()
                    )
        
        auth = "AWS %s:%s" % (self.access_key, signature)
        
        if not date_set:
            return auth, date_str
        return auth
    
    def _get_headers(self, authorization, date_str, **kwargs):
        headers = {
                   'Authorization': authorization,
                   'Date': date_str,
                   }
        headers.update(kwargs)
        
        return headers
    
    def _get_canonicalized_resource(self, bucket_name='', obj_name=''):
        path = '/'
        if bucket_name:
            path += bucket_name
        if bucket_name and obj_name:
            if not obj_name.startswith('/'):
                path += '/'
            path += obj_name
        elif bucket_name and not path.endswith('/'):
            path += '/'
            
        return path
    
    def _get_canoicalized_amz_headers(self, headers):
        amz_headers = [(k.lower(), v) for k, v in headers.iteritems() 
                       if k.lower().startswith('x-amz-')]
        amz_headers.sort()
        return ''.join(['%s:%s' % (k, v) for k, v in amz_headers])
    
    def _base_oper(self, url, headers, try_times=3, try_interval=3):
        def _get_data():
            try:
                req = urllib2.Request(url, headers=headers)
                resp = urllib2.urlopen(req)
                return resp.read()
            except urllib2.HTTPError, e:
                tree = XML.loads(e.read())
                raise S3Error(tree, e.code)
            
        for i in range(try_times):
            try:
                return _get_data()
            except urllib2.URLError:
                time.sleep(try_interval)
                
        raise S3Error(None, -1, "Can't connect to server")
    
    def put_bucket(self, bucket_name, x_amz_acl=X_AMZ_ACL.private):
        date_str = self._get_date_str()
        
        #kwargs = {'x-amz-acl': x_amz_acl }
        res = self._get_canonicalized_resource(bucket_name)
        sig = self._get_authorization('PUT', date_str=date_str, canonicalized_resource=res)
        headers = self._get_headers(sig, date_str)#, **kwargs)
            
        #headers['Host'] = '%s.s3.amazonaws.com' % bucket_name
        
        print self._base_oper(end_point, headers)
        
    def list_buckets(self):
        date_str = self._get_date_str()
        
        sig = self._get_authorization('GET', date_str=date_str)
        headers = self._get_headers(sig, date_str)#, **kwargs)
        print headers
        print self._base_oper(end_point, headers)
        
if __name__ == "__main__":
    from CloudBackup.test.settings import *
    
    client = S3Client(S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY)
    #client.put_bucket('chine-s3-test-1')
    client.list_buckets()    