#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-4-18

@author: Chine
'''

__author__ = "Chine King"
__description__ = "Errors for CloudBackup libraries"

class CloudBackupLibError(Exception):
    '''
    A base error for CloudBackup library
    :param src: the source of error, vdisk etc
    :param error_no: the number of the error source
    :param msg: the error message
    '''
    
    def __init__(self, src, err_no, msg):
        self.src = src
        self.err_no = int(err_no)
        self.msg = msg
        
    def __str__(self):
        if self.err_no == -1:
            return "Error from %s: %s" \
                    % (self.src, self.msg)
            
        return "Error from %s: %d, %s" \
                % (self.src, self.err_no, self.msg)
                
class VdiskError(CloudBackupLibError):
    '''
    Vdisk error
    '''
    
    def __init__(self, err_no, msg):
        super(CloudBackupLibError, self).__init__("vdisk", err_no, msg)