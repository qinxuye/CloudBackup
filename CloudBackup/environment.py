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

from CloudBackup.lib.vdisk import VdiskClient, CryptoVdiskClient
from CloudBackup.lib.s3 import S3Client, CryptoS3Client
from CloudBackup.lib.gs import GSClient, CryptoGSClient
from CloudBackup.lib.errors import VdiskError, S3Error, GSError
from CloudBackup.cloud import VdiskStorage, S3Storage, GSStorage
from CloudBackup.local import SyncHandler, S3SyncHandler, VdiskRefreshToken
from CloudBackup.errors import CloudBackupError
from CloudBackup.utils import win_hide_file, get_log_path, ensure_folder_exsits
from CloudBackup.test.settings import VDISK_APP_KEY, VDISK_APP_SECRET

DEFAULT_SLEEP_MINUTS = 1
DEFAULT_SLEEP_SECS = DEFAULT_SLEEP_MINUTS * 60

OFFSET = 3

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
                
                self.save_vdisk_info(account, password, is_weibo, log, encrypt, encrypt_code)
                return handler
            except VdiskError, e:
                raise CloudBackupError(e.src, e.err_no, e.msg)
        finally:
            self.vdisk_lock.release()
            
    def stop_vdisk(self):
        try:
            self.vdisk_lock.acquire()
            
            if self.vdisk_handler is None:
                return
            
            self.vdisk_handler.stop()
            self.vdisk_handler = None
            self.vdisk_token_refresh.stop()
            self.vdisk_token_refresh = None
            
            self.remove_vdisk_info()
        finally:
            self.vdisk_lock.release()
            
    def save_vdisk_info(self, account, password, is_weibo=False, 
                           log=True, encrypt=False, encrypt_code=None, offset=OFFSET):
        
        if self.vdisk_handler is None:
            return
        
        log_path = get_log_path()
        ensure_folder_exsits(log_path)
        save_file = os.path.join(log_path, '.vdisk.setting.txt')
        
        args = locals()
        
        fp = open(save_file, 'w')
        try:
            for arg in ('account', 'password',
                        'is_weibo', 'log', 'encrypt', 'encrypt_code'):
                if arg == 'password':
                    args['password'] = ','.join((str(ord(l) + offset) for l in args.pop('password')))
                
                fp.write(arg + '\t' + str(args[arg]) + '\n')
                
            win_hide_file(save_file)
        finally:
            fp.close()
            
    def load_vdisk_info(self, offset=OFFSET):
        
        save_file = os.path.join(get_log_path(), '.vdisk.setting.txt')
        
        if not os.path.exists(save_file):
            return
        
        args = {}
        
        fp = open(save_file, 'r')
        try:
            for line in fp.readlines():
                arg, content = line.strip().split('\t')
                if arg == 'password':
                    args['password'] = ''.join((chr(int(l) - offset) \
                                                for l in content.split(',')))
                elif arg == 'is_weibo' or arg == 'log' or arg == 'encrypt':
                    args[arg] = bool(content)
                elif arg == 'encrypt_code':
                    args[arg] = None if content == 'None' else content
                else:
                    args[arg] = content
                    
            return args
        finally:
            fp.close()
            
    def remove_vdisk_info(self):
        save_file = os.path.join(get_log_path(), '.vdisk.setting.txt')
        
        if not os.path.exists(save_file):
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
                return handler
            except S3Error, e:
                raise CloudBackupError(e.src, e.err_no, e.msg)
        finally:
            self.s3_lock.release()
            
    def stop_s3(self):
        try:
            self.s3_lock.acquire()
            
            if self.s3_handler is None:
                return
            
            self.s3_handler.stop()
            self.s3_handler = None
            
            self.remove_s3_info()
        finally:
            self.s3_lock.release()
            
    def save_s3_info(self, access_key, secret_access_key,
                           log=True, encrypt=False, encrypt_code=None):
        
        if self.s3_handler is None:
            return
        
        log_path = get_log_path()
        ensure_folder_exsits(log_path)
        save_file = os.path.join(log_path, '.s3.setting.txt')
        
        args = locals()
        
        fp = open(save_file, 'w')
        try:
            for arg in ('access_key', 'secret_access_key',
                        'log', 'encrypt', 'encrypt_code'):
                fp.write(arg + '\t' + str(args[arg]) + '\n')
                
            win_hide_file(save_file)
        finally:
            fp.close()
            
    def load_s3_info(self):
        
        save_file = os.path.join(get_log_path(), '.s3.setting.txt')
        
        if not os.path.exists(save_file):
            return
        
        args = {}
        
        fp = open(save_file, 'r')
        try:
            for line in fp.readlines():
                arg, content = line.strip().split('\t')
                
                if arg == 'log' or arg == 'encrypt':
                    args[arg] = bool(content)
                elif arg == 'encrypt_code':
                    args[arg] = None if content == 'None' else content
                else:
                    args[arg] = content
                    
            return args
        finally:
            fp.close()
            
    def remove_s3_info(self):
        save_file = os.path.join(get_log_path(), '.s3.setting.txt')
        
        if not os.path.exists(save_file):
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
                return handler
            except GSError, e:
                raise CloudBackupError(e.src, e.err_no, e.msg)
        finally:
            self.gs_lock.release()
            
    def stop_gs(self):
        try:
            self.gs_lock.acquire()
            
            if self.gs_handler is None:
                return
            
            self.gs_handler.stop()
            self.gs_handler = None
            
            self.remove_gs_info()
        finally:
            self.gs_lock.release()
            
    def save_gs_info(self, access_key, secret_access_key, project_id,
                           log=True, encrypt=False, encrypt_code=None):
        
        if self.gs_handler is None:
            return
        
        log_path = get_log_path()
        ensure_folder_exsits(log_path)
        save_file = os.path.join(log_path, '.gs.setting.txt')
        
        args = locals()
        
        fp = open(save_file, 'w')
        try:
            for arg in ('access_key', 'secret_access_key', 'project_id'
                        'log', 'encrypt', 'encrypt_code'):
                fp.write(arg + '\t' + str(args[arg]) + '\n')
                
            win_hide_file(save_file)
        finally:
            fp.close()
            
    def load_gs_info(self):
        
        save_file = os.path.join(get_log_path(), '.gs.setting.txt')
        
        if not os.path.exists(save_file):
            return
        
        args = {}
        
        fp = open(save_file, 'r')
        try:
            for line in fp.readlines():
                arg, content = line.strip().split('\t')
                
                if arg == 'log' or arg == 'encrypt':
                    args[arg] = bool(content)
                elif arg == 'encrypt_code':
                    args[arg] = None if content == 'None' else content
                else:
                    args[arg] = content
                    
            return args
        finally:
            fp.close()
            
    def remove_gs_info(self):
        save_file = os.path.join(get_log_path(), '.gs.setting.txt')
        
        if not os.path.exists(save_file):
            os.remove(save_file)