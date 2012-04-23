#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-4-20

@author: Chine
'''

import pyDes

__author__ = "Chine King"
__description__ = "crypto modules, DES requires for pyDes."

class DES(object):
    def __init__(self, IV):
        '''
        :param IV: initial value, length must be 8 bytes
        '''
        
        assert isinstance(IV, str)
        assert len(IV) == 8
        
        self.IV = IV
        self.des = pyDes.des("DESCRYPT", pyDes.CBC, self.IV, pad=None, padmode=pyDes.PAD_PKCS5)
        
    def encrypt(self, data):
        return self.des.encrypt(data)
        
    def decrypt(self, data):
        return self.des.decrypt(data)