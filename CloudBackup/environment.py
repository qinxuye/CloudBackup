#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-5-19

@author: Chine
'''

from CloudBackup.lib.vdisk import VdiskClient, CryptoVdiskClient
from CloudBackup.lib.s3 import S3Client, CryptoS3Client
from CloudBackup.lib.gs import GSClient, CryptoGSClient
from CloudBackup.lib.errors import VdiskError, S3Error, GSError
from CloudBackup.cloud import VdiskStorage, S3Storage, GSStorage
from CloudBackup.local import SyncHandler, S3SyncHandler
from CloudBackup.errors import CloudBackupError
from CloudBackup.test.settings import VDISK_APP_KEY, VDISK_APP_SECRET

DEFAULT_SLEEP_MINUTS = 1
DEFAULT_SLEEP_SECS = DEFAULT_SLEEP_MINUTS * 60

class Environment(object):
    instance = None
    vdisk_handler = None
    s3_handler = None
    gs_handler = None
    
    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(Environment, cls).__new__(
                            cls, *args, **kwargs)
        return cls.instance
    
    def setup_vdisk(self, account, password, local_folder, holder,
                     is_weibo=False, log=True, encrypt=False, encrypt_code=None):
        if self.vdisk_handler:
            return self.vdisk_handler
        
        if encrypt and encrypt_code:
            client = CryptoVdiskClient(VDISK_APP_KEY, VDISK_APP_SECRET)
            client.auth(account, password, encrypt_code, 'sinat' if is_weibo else 'local')
        else:
            client = VdiskClient(VDISK_APP_KEY, VDISK_APP_SECRET)
            client.auth(account, password, 'sinat' if is_weibo else 'local')
            
        storage = VdiskStorage(client, holder_name=holder)
        
        try:
            handler = SyncHandler(storage, local_folder, sec=DEFAULT_SLEEP_SECS, log=log)
            handler.start()
            self.vdisk_handler = handler
            return handler
        except VdiskError, e:
            raise CloudBackupError(e.src, e.err_no, e.msg)
        
    def setup_s3(self, access_key, secret_access_key, local_folder, holder,
                 log=True, encrypt=False, encrypt_code=None):
        if self.s3_handler:
            return self.s3_handler
        
        if encrypt and encrypt_code:
            client = CryptoS3Client(access_key, secret_access_key, encrypt_code)
        else:
            client = S3Client(access_key, secret_access_key)
            
        storage = S3Storage(client, holder)
        
        try:
            handler = S3SyncHandler(storage, local_folder, sec=DEFAULT_SLEEP_SECS, log=log)
            handler.start()
            self.s3_handler = handler
            return handler
        except S3Error, e:
            raise CloudBackupError(e.src, e.err_no, e.msg)
        
    def setup_gs(self, access_key, secret_access_key, project_id, local_folder, holder,
                 log=True, encrypt=False, encrypt_code=None):
        if self.gs_handler:
            return self.gs_handler
        
        if encrypt and encrypt_code:
            client = CryptoGSClient(access_key, secret_access_key, project_id, encrypt_code)
        else:
            client = GSClient(access_key, secret_access_key, project_id)
            
        storage = GSStorage(client, holder)
        
        try:
            handler = SyncHandler(storage, local_folder, sec=DEFAULT_SLEEP_SECS, log=log)
            handler.start()
            self.gs_handler = handler
            return handler
        except GSError, e:
            raise CloudBackupError(e.src, e.err_no, e.msg)