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

__author__ = "Chine King"
__description__ = "A client for Amazon S3 api, site: http://aws.amazon.com/documentation/s3/"

ACTION_TYPES = ('PUT', 'GET', 'DELETE')
GMT_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

class S3Client(object):
    def __init__(self, access_key, secret_access_key):
        self.access_key = access_key
        self.secret_key = secret_access_key
        
    def _get_authorization(self, 
                           action, 
                           content_md5,
                           content_type,
                           date_str,
                           canonicalized_amz_headers,
                           canonicalized_resource):
        
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
    
    