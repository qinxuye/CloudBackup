#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-4-18

@author: Chine
'''

__author__ = "Chine King"

import hmac
from hashlib import sha256
import time
import mimetypes

from errors import CloudBackupLibError

def hmac_sha256(secret, data):
    return hmac.new(secret, data, sha256).hexdigest()

def encode_multipart(kwargs):
    '''
    Build a multipart/form-data body with generated random boundary.
    '''
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    
    for k, v in kwargs.iteritems():
        data.append('--%s' % boundary)
        if hasattr(v, 'read'):
            # file-like object:
            filename = getattr(v, 'name', '')
            content = v.read()
            file_type = mimetypes.guess_type(filename)
            if file_type is None:
                raise CloudBackupLibError('utils', -1, 'Could not determine file type')
            file_type = file_type[0]
            
            data.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (k, filename))
            data.append('Content-Length: %d' % len(content))
            data.append('Content-Type: %s\r\n' % file_type)
            data.append(content)
        else:
            data.append('Content-Disposition: form-data; name="%s"\r\n' % k)
            data.append(v.encode('utf-8') if isinstance(v, unicode) else str(v))
    data.append('--%s--\r\n' % boundary)
    return '\r\n'.join(data), boundary