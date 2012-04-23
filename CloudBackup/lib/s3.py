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

from errors import S3Error
from utils import XML

__author__ = "Chine King"
__description__ = "A client for Amazon S3 api, site: http://aws.amazon.com/documentation/s3/"

ACTION_TYPES = ('PUT', 'GET', 'DELETE')
GMT_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

class XAmzAcl(object):
    def __init__(self):
        for val in ('private', 'public-read', 'public-read-write', 
                    'authenticated-read', 'bucket-owner-read', 
                    'bucket-owner-full-control'):
            setattr(self, val.replace('-', '_'), val)

class S3Client(object):
    def __init__(self, access_key, secret_access_key):
        self.access_key = access_key
        self.secret_key = secret_access_key
        
    def _get_authorization(self, 
                           action, 
                           date_str,
                           content_md5='',
                           content_type='',
                           canonicalized_amz_headers='',
                           canonicalized_resource=''):
        
        assert action in ACTION_TYPES # action must be put, get and delete
        
        string_to_sign = '%s\n%s\n%s\n%s\n%s%s' % (action,
                                                   content_md5,
                                                   content_type,
                                                   date_str,
                                                   canonicalized_amz_headers,
                                                   canonicalized_resource
                                                   )
        signature = base64.encodestring(
                        hmac.new(self.access_key, string_to_sign, hashlib.sha1).digest()
                    )
        return "AWS %s:%s" % (self.access_key, signature)
    
    def _get_date_str(self):
        return datetime.datetime.utcnow().strftime(GMT_FORMAT)
    
    def _get_headers(self, authorization, date_str, **kwargs):
        headers = {
                   'Authorization': authorization,
                   'Date': date_str
                   }
        headers.update(kwargs)
        
        return headers
    
    def _base_oper(self, url, headers):
        try:
            req = urllib2.Request(url, headers=headers)
            resp = urllib2.urlopen(req)
            return resp.read()
        except urllib2.HTTPError, e:
            tree = XML.loads(e.read())
            raise S3Error(tree, e.code)
    
    def put_bucket(self, bucket_name, x_amz_acl='private'):
        date_str = self._get_date_str()
        
        if x_amz_acl != 'private':
            kwargs = {'x-amz-acl': x_amz_acl }
            headers = self._get_headers(self._get_authorization('PUT', date_str), date_str, **kwargs)
        else:
            headers = self._get_headers(self._get_authorization('PUT', date_str), date_str)
            
        headers['Host'] = '%s.s3.amazonaws.com' % bucket_name
        
        print self._base_oper('http://s3.amazonaws.com', headers)
        
if __name__ == '__main__':
    client = S3Client('AKIAILIXLRD4XN3RMPKA', 'g2FoEFDoQMz8n5dNP8k1FRzqkC8VoN4DURg4hYBU')
    client.put_bucket('chine-test-bucket-1')
            
        