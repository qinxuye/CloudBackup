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

Created on 2012-5-10

@author: Chine
'''

import threading
import os
import time
import hashlib

from cloud import Storage, S3Storage
from utils import join_local_path, get_sys_encoding
from CloudBackup.log import Log
from CloudBackup.lib.vdisk import VdiskClient

SPACE_REPLACE = '#$&'
DEFAULT_SLEEP_MINUTS = 5
DEFAULT_SLEEP_SECS = DEFAULT_SLEEP_MINUTS * 60

class FileEntry(object):
    def __init__(self, path, timestamp, md5):
        self.path = path
        self.timestamp = timestamp
        self.md5 = md5
        
class VdiskRefreshToken(threading.Thread):
    stopped = False
    def __init__(self, client):
        assert isinstance(client, VdiskClient)
        super(VdiskRefreshToken, self).__init__()
        self.client = client
        
    def refresh_token(self):
        self.client.keep_token()
        
    def stop(self):
        self.stopped = True
        
    def run(self, sleep_minutes=10):
        while not self.stopped:
            self.refresh_token()
            time.sleep(sleep_minutes * 60)

class SyncHandler(threading.Thread):
    stopped = False
    
    def __init__(self, storage, folder_name, 
                 loop=True, sec=DEFAULT_SLEEP_SECS, log=False, log_obj=None):
        super(SyncHandler, self).__init__()
        
        assert isinstance(storage, Storage)
        self.storage = storage
        self.folder_name = folder_name
        
        self.loop = loop
        self.sec = sec
        
        self.encoding = get_sys_encoding()
        self.calc_md5 = lambda data: hashlib.md5(data).hexdigest()
        
        self.log = log
        if log and log_obj:
            self.log_obj = log_obj
        elif log:
            log_file = os.path.join(self.folder_name,
                '.%s.log.txt' % self.storage.__class__.__name__.rsplit('Storage')[0].lower())
            self.log_obj = Log(log_file)
    
    def local_to_cloud(self, path, timestamp):
        splits = path.rsplit('.', 1)
        
        if len(splits) == 1:
            splits.append(str(timestamp))
        else:
            splits.insert(-1, str(timestamp))
        return '.'.join(splits).replace(' ', SPACE_REPLACE)
    
    def cloud_to_local(self, path):
        path = path.replace(SPACE_REPLACE, ' ')
        splits = path.rsplit('.', 2)
        
        if len(splits) == 2:
            try:
                timestamp = int(splits.pop(-1))
                return splits[0], timestamp
            except ValueError:
                return path, -1
        elif len(splits) == 3:
            try:
                timestamp = int(splits.pop(-2))
                return '.'.join(splits), timestamp
            except ValueError:
                return path, -1
        else:
            return path, -1
        
    def list_cloud(self, cloud_path, recursive=False):
        for f in self.storage.list(cloud_path, recursive):
            f.cloud_path = f.path
            
            path, _ = self.cloud_to_local(f.path)
            path = path.encode('utf-8')
            f.path = path
            yield f
            
    def _get_cloud_files(self):
        files = {}
        for f in self.storage.list_files('', True):
            path, timestamp = self.cloud_to_local(f.path)
            path = path.encode('utf-8')
            files[path] = FileEntry(f.path, timestamp, f.md5)
            
        return files
            
    def _get_local_files(self):
        files = {}
        
        folder_name = self.folder_name if self.folder_name.endswith(os.sep) \
                        else self.folder_name+os.sep
        
        for dirpath, dirnames, filenames in os.walk(self.folder_name):
            for filename in filenames:
                if filename.startswith('.'):
                    continue
                
                abs_filename = os.path.join(dirpath, filename)
                rel_path = abs_filename.split(folder_name, 1)[1]
                rel_path = rel_path.decode(self.encoding).encode('utf-8')
                timestamp = int(os.path.getmtime(abs_filename))
                fp = open(abs_filename, 'rb')
                
                try:
                    md5 = self.calc_md5(fp.read())
                    
                    entry = FileEntry(abs_filename, timestamp, md5)
                    
                    if os.sep == '/':
                        files[rel_path] = entry
                    else:
                        files[rel_path.replace(os.sep, '/')] = entry
                finally:
                    fp.close()
                    
        return files
    
    def _upload(self, f, local_files_tm, cloud_files_tm):
        entry = local_files_tm[f]
        filename, timestamp = entry.path, entry.timestamp
        cloud_path = self.local_to_cloud(f, timestamp)
        self.storage.upload(cloud_path, filename)
        
        if self.log:
            self.log_obj.write('Upload file: %s' % f)
        
    def _download(self, f, local_files_tm, cloud_files_tm):
        filename = join_local_path(self.folder_name, 
                                   f.decode('utf-8').encode(self.encoding))
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        
        cloud_path = cloud_files_tm[f].path
        self.storage.download(cloud_path, filename)
        
        if self.log:
            self.log_obj.write('Download file: %s' % f)
    
    def sync(self):
        local_files_tm = self._get_local_files()
        cloud_files_tm = self._get_cloud_files()
        
        local_files = set(local_files_tm.keys())
        cloud_files = set(cloud_files_tm.keys())
        
        for f in (local_files - cloud_files):
            self._upload(f, local_files_tm, cloud_files_tm)
            
        for f in (cloud_files - local_files):
            self._download(f, local_files_tm, cloud_files_tm)
            
        for f in (cloud_files & local_files):
            local_entry = local_files_tm[f]
            cloud_entry = cloud_files_tm[f]
            
            if local_entry.md5 != cloud_entry.md5:
                if local_entry.timestamp < cloud_entry.timestamp:
                    self._download(f, local_files_tm, cloud_files_tm)
                elif local_entry.timestamp > cloud_entry.timestamp:
                    self._upload(f, local_files_tm, cloud_files_tm)
    
    def stop(self):
        self.stopped = True
        
    def run(self):
        self.sync()        
        if self.loop and not self.stopped:
            time.sleep(self.sec)
            self.sync()
            
class S3SyncHandler(SyncHandler):
    def __init__(self, storage, folder_name, loop=True, sec=DEFAULT_SLEEP_SECS, 
                 log=False, log_obj=None):
        super(S3SyncHandler, self).__init__(storage, folder_name, loop, sec, log, log_obj)
        
        assert isinstance(storage, S3Storage)
        
    def list_cloud(self, cloud_path, recursive=False):
        for f in self.storage.list(cloud_path, recursive):
            f.cloud_path = f.path
            
            path, _ = self.cloud_to_local(f.path)
            if isinstance(path, str):
                path = path.decode('raw-unicode-escape').encode('utf-8')
            elif isinstance(path, unicode):
                path = path.encode('utf-8')
            f.path = path
            
            yield f    
        
    def _get_cloud_files(self):
        files = {}
        for f in self.storage.list_files('', True):
            path, timestamp = self.cloud_to_local(f.path)
            if isinstance(path, str):
                path = path.decode('raw-unicode-escape').encode('utf-8')
            elif isinstance(path, unicode):
                path = path.encode('utf-8')
            files[path] = FileEntry(f.path, timestamp, f.md5)
            
        return files
    
    def _upload(self, f, local_files_tm, cloud_files_tm):
        entry = local_files_tm[f]
        filename, timestamp = entry.path, entry.timestamp
        f = f.decode('utf-8').encode('raw-unicode-escape')
        cloud_path = self.local_to_cloud(f, timestamp)
        self.storage.upload(cloud_path, filename)
        
        if self.log:
            self.log_obj.write('Upload file: %s' % f)
            