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

Created on 2012-4-18

@author: Chine
'''

__author__ = "Chine King"

import hmac
from hashlib import sha256, sha1, md5
from base64 import b64encode
import time
import mimetypes
try:
    from xml.etree.ElementTree import XMLTreeBuilder
except ImportError:
    from elementtree.ElementTree import XMLTreeBuilder

from errors import CloudBackupLibError

def iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False

def hmac_sha256_hex(secret, data):
    return hmac.new(secret, data, sha256).hexdigest()

def hmac_sha1(secret, data):
    return b64encode(hmac.new(secret, data, sha1).digest())

def calc_md5(data):
    return b64encode(md5(data).digest())

def encode_multipart(kwargs, encrypt=False, encrypt_func=None):
    '''
    Build a multipart/form-data body with generated random boundary.
    '''
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    
    for k, v in kwargs.iteritems():
        data.append('--%s' % boundary)
        if hasattr(v, 'read') or \
            (isinstance(v, tuple) and len(v) == 2 and hasattr(v[0], 'read')):
            # file-like object:
            if isinstance(v, tuple):
                filename = v[1]
                v = v[0]
            else:
                filename = getattr(v, 'name', '')
            content = v.read()
            if encrypt and encrypt_func is not None:
                content = encrypt_func(content)
            
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

class NamespaceFixXmlTreeBuilder(XMLTreeBuilder):
    def _fixname(self, key):
        if '}' in key:
            key = key.split('}', 1)[1]
        return key
    
class XML(object):
    @classmethod
    def loads(cls, data):
        parser = NamespaceFixXmlTreeBuilder()
        parser.feed(data)
        return parser.close()