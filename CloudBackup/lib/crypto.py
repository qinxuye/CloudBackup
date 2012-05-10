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