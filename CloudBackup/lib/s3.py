#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-4-20

@author: Chine
'''

import datetime
import urllib2
import time
import mimetypes

from errors import S3Error
from utils import XML, hmac_sha1, calc_md5

__author__ = "Chine King"
__description__ = "A client for Amazon S3 api, site: http://aws.amazon.com/documentation/s3/"

ACTION_TYPES = ('PUT', 'GET', 'DELETE')
GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
STRING_TO_SIGN = '''%(action)s
%(content_md5)s
%(content_type)s
%(date)s
%(c_amz_headers)s%(c_resource)s'''

end_point = "http://s3.amazonaws.com"

class XAmzAcl(object):
    def __init__(self):
        for val in ('private', 'public-read', 'public-read-write', 
                    'authenticated-read', 'bucket-owner-read', 
                    'bucket-owner-full-control'):
            setattr(self, val.replace('-', '_'), val)
X_AMZ_ACL = XAmzAcl()

class S3Request(object):
    def __init__(self, access_key, secret_access_key, 
                 action, bucket_name=None, obj_name=None,
                 data=None, content_type=None, metadata={}, amz_headers={} ):
        
        assert action in ACTION_TYPES # action must be put, get and delete
        
        self.access_key = access_key
        self.secret_key = secret_access_key
        self.action = action
        
        self.bucket_name = bucket_name
        self.obj_name = obj_name
        self.data = data
        
        self.content_type = content_type
        self._set_content_type()
        
        self.metadata = metadata
        self.amz_headers = amz_headers
        
        self.date_str = self._get_date_str()
            
    def _get_date_str(self):
        return datetime.datetime.utcnow().strftime(GMT_FORMAT)
    
    def _set_content_type(self):
        if self.obj_name is not None and not self.content_type:
            self.content_type = mimetypes.guess_type(self.obj_name)[0]
            
    def _get_canonicalized_resource(self):
        path = '/'
        if self.bucket_name:
            path += self.bucket_name
        if self.bucket_name and self.obj_name:
            if not self.obj_name.startswith('/'):
                path += '/'
            path += self.obj_name
        elif self.bucket_name and not path.endswith('/'):
            path += '/'
            
        return path
    
    def _get_canoicalized_amz_headers(self, headers):
        amz_headers = [(k.lower(), v) for k, v in headers.iteritems() 
                       if k.lower().startswith('x-amz-')]
        amz_headers.sort()
        return ''.join(['%s:%s' % (k, v) for k, v in amz_headers])
    
    def _get_authorization(self, headers):
        string_to_sign = STRING_TO_SIGN % {
                            'action': self.action,
                            'content_md5': headers.get('Content-MD5', ''),
                            'content_type': headers.get('Content-Type', ''),
                            'date': self.date_str,
                            'c_amz_headers': self._get_canoicalized_amz_headers(headers),
                            'c_resource': self._get_canonicalized_resource()
                         }
        signature = hmac_sha1(self.secret_key, string_to_sign)
        
        return "AWS %s:%s" % (self.access_key, signature)
    
    def get_headers(self):
        headers = { 
                   'Date': self.date_str
                   }
        if self.data:
            headers['Content-Length'] = len(self.data)
            headers['Content-MD5'] = calc_md5(self.data)
            
        if self.content_type is not None:
            headers['Content-Type'] = self.content_type
            
        if self.bucket_name:
            headers['Host'] = '%s.s3.amazonaws.com' % self.bucket_name
        
        for k, v in self.metadata.iteritems():
            headers['x-amz-meta-' + k] = v
        for k, v in self.amz_headers.iteritems():
            headers['x-amz-' + k] = v
            
        headers['Authorization'] = self._get_authorization(headers)
        return headers
    
    def submit(self, try_times=3, try_interval=3):
        def _get_data():
            headers = self.get_headers()
            try:
                opener = urllib2.build_opener(urllib2.HTTPHandler)
                req = urllib2.Request(end_point, data=self.data, headers=headers)
                req.get_method = lambda: self.action
                resp = opener.open(req)
                return resp.read()
            except urllib2.HTTPError, e:
                tree = XML.loads(e.read())
                raise S3Error(tree, e.code)
            
        for i in range(try_times):
            try:
                return _get_data()
            except urllib2.URLError:
                time.sleep(try_interval)
    
class S3Response(object):
    def __init__(self):
        pass

class S3Client(object):
    def __init__(self, access_key, secret_access_key):
        self.access_key = access_key
        self.secret_key = secret_access_key
        
    def list_buckets(self):
        req = S3Request(self.access_key, self.secret_key, 'GET')
        return req.submit()
    
    def put_bucket(self, bucket_name, x_amz_acl=X_AMZ_ACL.private):
        metadata = {}
        if x_amz_acl != X_AMZ_ACL.private:
            metadata['acl'] = x_amz_acl
        
        req = S3Request(self.access_key, self.secret_key, 'PUT', 
                        bucket_name=bucket_name, metadata=metadata)
        
        return req.submit()
        
if __name__ == "__main__":
    from CloudBackup.test.settings import *
    
    client = S3Client(S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY)
    print client.put_bucket('chine-s3-test-2')
    #print client.list_buckets()