#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-4-18

@author: Chine
'''

__author__ = "Chine King"

import hmac
from hashlib import sha256
from base64 import b64encode

def hmac_sha256(secret, data):
    #digest = hmac.new(secret, data, sha256).digest()
    #return b64encode(digest)
    return hmac.new(secret, data, sha256).hexdigest()