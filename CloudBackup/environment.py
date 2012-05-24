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

Created on 2012-5-19

@author: Chine
'''

import threading
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

from CloudBackup.lib.vdisk import VdiskClient, CryptoVdiskClient
from CloudBackup.lib.s3 import S3Client, CryptoS3Client
from CloudBackup.lib.gs import GSClient, CryptoGSClient
from CloudBackup.lib.errors import VdiskError, S3Error, GSError
from CloudBackup.lib.crypto import DES
from CloudBackup.cloud import VdiskStorage, S3Storage, GSStorage
from CloudBackup.local import SyncHandler, S3SyncHandler, VdiskRefreshToken
from CloudBackup.errors import CloudBackupError
from CloudBackup.utils import win_hide_file, get_info_path, ensure_folder_exsits
from CloudBackup.test.settings import VDISK_APP_KEY, VDISK_APP_SECRET

DEFAULT_SLEEP_MINUTS = 1
DEFAULT_SLEEP_SECS = DEFAULT_SLEEP_MINUTS * 60

OFFSET = 3

get_settings_path = lambda dirpath, setting_type: \
    os.path.join(dirpath, '.%s.setting' % setting_type)
encrypt = lambda s: ','.join((str(ord(l) + OFFSET) for l in s))
decrypt = lambda s: ''.join((chr(int(l) - OFFSET) for l in s.split(',')))
    
def serilize(file_obj, content, encrypt_func, *encrypt_fields):
    assert isinstance(content, dict)
    for field in encrypt_fields:
        if field in content:
            content[field] = encrypt_func(content.pop(field))
    pickle.dump(content, file_obj)
    
def unserilize(file_obj, decrypt_func, *decrypt_fields):
    file_obj.seek(0)
    content = pickle.load(file_obj)
    for field in decrypt_fields:
        if field in content:
            print 'done!'
            content[field] = decrypt_func(content.pop(field))
    return content

def save_info(info_type, content, encrypt_func, *encrypt_fields):
    folder_name = get_info_path()
    ensure_folder_exsits(folder_name)
    
    settings_path = get_settings_path(folder_name, info_type)
    file_obj = open(settings_path, 'w+')
    try:
        serilize(file_obj, content, encrypt_func, *encrypt_fields)
    finally:
        file_obj.close()
        
def get_info(info_type, decrypt_func, *decrypt_fields):
    folder_name = get_info_path()
    settings_path = get_settings_path(folder_name, info_type)
    
    if not os.path.exists(settings_path):
        return
    
    file_obj = open(settings_path, 'r')
    try:
        return unserilize(file_obj, decrypt_func, *decrypt_fields)
    finally:
        file_obj.close()

class Environment(object):
    instance = None
    
    vdisk_handler = None
    vdisk_lock = threading.Lock()
    vdisk_token_refresh = None
    
    s3_handler = None
    s3_lock = threading.Lock()
    
    gs_handler = None
    gs_lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(Environment, cls).__new__(
                            cls, *args, **kwargs)
        return cls.instance
    
    def _get_iv(self, astr):
        if len(astr) >= 8:
            iv = astr[:8]
        else:
            iv = astr + '*' * (8 - len(astr))
        return iv
    
    def _get_encrypt(self, iv):
        des = DES(iv)
        return des.encrypt
    
    def _get_decrypt(self, iv):
        des = DES(iv)
        return des.decrypt
    
    def setup_vdisk(self, account, password, local_folder, holder, is_weibo=False, 
                    log=True, encrypt=False, encrypt_code=None, force_stop=True):
        try:
            self.vdisk_lock.acquire()
            
            if not force_stop and self.vdisk_handler:
                return self.vdisk_handler
            
            if force_stop and self.vdisk_handler:
                self.vdisk_handler.stop()
            
            if encrypt and encrypt_code:
                client = CryptoVdiskClient(VDISK_APP_KEY, VDISK_APP_SECRET)
                client.auth(account, password, encrypt_code, 'sinat' if is_weibo else 'local')
            else:
                client = VdiskClient(VDISK_APP_KEY, VDISK_APP_SECRET)
                client.auth(account, password, 'sinat' if is_weibo else 'local')
            self.vdisk_token_refresh = VdiskRefreshToken(client)
            self.vdisk_token_refresh.start()
                
            storage = VdiskStorage(client, holder_name=holder)
            
            try:
                handler = SyncHandler(storage, local_folder, sec=DEFAULT_SLEEP_SECS, log=log)
                handler.start()
                self.vdisk_handler = handler
                
                self.save_vdisk_info(account, password, local_folder, holder,
                                     is_weibo, log, encrypt, encrypt_code)
                return handler
            except VdiskError, e:
                raise CloudBackupError(e.src, e.err_no, e.msg)
        finally:
            self.vdisk_lock.release()
            
    def stop_vdisk(self, clear_info=True):
        try:
            self.vdisk_lock.acquire()
            
            if self.vdisk_handler is None:
                return
            
            self.vdisk_handler.stop()
            self.vdisk_handler = None
            self.vdisk_token_refresh.stop()
            self.vdisk_token_refresh = None
            
            if clear_info:
                self.remove_vdisk_info()
        finally:
            self.vdisk_lock.release()
            
    def save_vdisk_info(self, account, password, local_folder, holder,
                        is_weibo=False, log=True, encrypt=False, encrypt_code=None):
        
        if self.vdisk_handler is None:
            return
        
        args = locals()
        del args['self']
        
        save_info('vdisk', args, self._get_encrypt(self._get_iv(account)), 'password')
            
    def load_vdisk_info(self):
        info = get_info('vdisk', lambda s: s)
        if info is None:
            return
        info['password'] = self._get_decrypt(self._get_iv(info['account']))(info.pop('password'))
        return info
            
    def remove_vdisk_info(self):
        save_file = get_settings_path(get_info_path(), 'vdisk')
        
        if os.path.exists(save_file):
            os.remove(save_file)
        
    def setup_s3(self, access_key, secret_access_key, local_folder, holder,
                 log=True, encrypt=False, encrypt_code=None, force_stop=True):
        try:
            self.s3_lock.acquire()
        
            if self.s3_handler:
                return self.s3_handler
            
            if force_stop and self.s3_handler:
                self.s3_handler.stop()
            
            if encrypt and encrypt_code:
                client = CryptoS3Client(access_key, secret_access_key, encrypt_code)
            else:
                client = S3Client(access_key, secret_access_key)
                
            storage = S3Storage(client, holder)
            
            try:
                handler = S3SyncHandler(storage, local_folder, sec=DEFAULT_SLEEP_SECS, log=log)
                handler.start()
                self.s3_handler = handler
                
                self.save_s3_info(access_key, secret_access_key, local_folder, holder, 
                                  log, encrypt, encrypt_code)
                
                return handler
            except S3Error, e:
                raise CloudBackupError(e.src, e.err_no, e.msg)
        finally:
            self.s3_lock.release()
            
    def stop_s3(self, clear_info=True):
        try:
            self.s3_lock.acquire()
            
            if self.s3_handler is None:
                return
            
            self.s3_handler.stop()
            self.s3_handler = None
            
            if clear_info:
                self.remove_s3_info()
        finally:
            self.s3_lock.release()
            
    def save_s3_info(self, access_key, secret_access_key, local_folder, holder,
                           log=True, encrypt=False, encrypt_code=None):
        
        if self.s3_handler is None:
            return
        
        args = locals()
        del args['self']
        
        save_info('s3', args, lambda s: s)
            
    def load_s3_info(self):
        info = get_info('s3', lambda s: s)
        return info
            
    def remove_s3_info(self):
        save_file = get_settings_path(get_info_path(), 's3')
        
        if os.path.exists(save_file):
            os.remove(save_file)
        
    def setup_gs(self, access_key, secret_access_key, project_id, local_folder, holder,
                 log=True, encrypt=False, encrypt_code=None, force_stop=True):
        try:
            self.gs_lock.acquire()
        
            if self.gs_handler:
                return self.gs_handler
            
            if force_stop and self.gs_handler:
                self.gs_handler.stop()
            
            if encrypt and encrypt_code:
                client = CryptoGSClient(access_key, secret_access_key, project_id, encrypt_code)
            else:
                client = GSClient(access_key, secret_access_key, project_id)
                
            storage = GSStorage(client, holder)
            
            try:
                handler = SyncHandler(storage, local_folder, sec=DEFAULT_SLEEP_SECS, log=log)
                handler.start()
                self.gs_handler = handler
                
                self.save_gs_info(access_key, secret_access_key, project_id, 
                                  local_folder, holder, log, encrypt, encrypt_code)
                
                return handler
            except GSError, e:
                raise CloudBackupError(e.src, e.err_no, e.msg)
        finally:
            self.gs_lock.release()
            
    def stop_gs(self, clear_info=True):
        try:
            self.gs_lock.acquire()
            
            if self.gs_handler is None:
                return
            
            self.gs_handler.stop()
            self.gs_handler = None
            
            if clear_info:
                self.remove_gs_info()
        finally:
            self.gs_lock.release()
            
    def save_gs_info(self, access_key, secret_access_key, project_id,
                     local_folder, holder,
                     log=True, encrypt=False, encrypt_code=None):
        
        if self.gs_handler is None:
            return
        
        args = locals()
        del args['self']
        
        save_info('gs', args, lambda s: s)
            
    def load_gs_info(self):
        info = get_info('gs', lambda s: s)
        return info
            
    def remove_gs_info(self):
        save_file = get_settings_path(get_info_path(), 'gs')
        
        if os.path.exists(save_file):
            os.remove(save_file)