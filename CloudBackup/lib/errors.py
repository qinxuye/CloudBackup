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
__description__ = "Errors for CloudBackup libraries"

class CloudBackupLibError(Exception):
    '''
    A base error for CloudBackup library
    '''
    
    def __init__(self, src, err_no, msg):
        '''
        :param src: the source of error, vdisk etc
        :param error_no: the number of the error source
        :param msg: the error message
        '''
        
        self.src = src
        self.err_no = int(err_no)
        self.msg = msg
        
    def __str__(self):
        if self.err_no < 0:
            return "Error from %s: %s" \
                    % (self.src, self.msg)
            
        return "Error from %s: %d, %s" \
                % (self.src, self.err_no, self.msg)
                
class VdiskError(CloudBackupLibError):
    '''
    Vdisk error
    '''
    
    def __init__(self, err_no, msg):
        super(VdiskError, self).__init__('vdisk', err_no, msg)
        
class S3Error(CloudBackupLibError):
    '''
    Amazon S3 error
    '''
    
    def __init__(self, status, tree=None, msg=None):
        self.src = 's3'
        self.err_no = status
        
        if tree:
            self.tree = tree
            self._parse()
        elif msg:
            self.msg = msg
        
    def _parse(self, tree=None):
        if not tree:
            tree = self.tree
        
        for tag_name in ('Code', 'Message', 'RequestId', 'Resource', 'Details'):
            tag = tree.find(tag_name)
            if hasattr(tag, 'text'):
                if tag_name == 'Message':
                    self.msg = tag.text
                else:
                    setattr(self, tag_name.lower(), tag.text)
                    
class GSError(S3Error):
    '''
    Google Cloud Storage error.
    '''
    
    def __init__(self, status, tree=None, msg=None):
        super(GSError, self).__init__(status, tree, msg)
        self.src = 'Google Cloud Storage'