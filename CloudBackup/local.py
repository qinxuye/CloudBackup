#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-5-10

@author: Chine
'''

import threading
import os
import time

from cloud import Storage
from utils import join_local_path

class SyncHandler(threading.Thread):
    def __init__(self, storage, folder_name, loop=True, sec=300):
        super(SyncHandler, self).__init__()
        
        assert isinstance(storage, Storage)
        self.storage = storage
        self.folder_name = folder_name
        
        self.loop = loop
        self.sec = sec
    
    def _add_timestamp_to_filename(self, path, timestamp):
        splits = path.rsplit('.', 1)
        
        if len(splits) == 1:
            splits.append(str(timestamp))
        else:
            splits.insert(-1, str(timestamp))
        return '.'.join(splits)
    
    def _remove_timestamp_from_filename(self, path):
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
            
    def _get_cloud_files(self):
        files = {}
        for f in self.storage.list_files(''):
            path, timestamp = self._remove_timestamp_from_filename(f.path)
            files[path] = timestamp
            
        return files
            
    def _get_local_files(self):
        files = {}
        
        folder_name = self.folder_name if self.folder_name.endswith(os.sep) \
                        else self.folder_name+os.sep
        
        for dirpath, dirnames, filenames in os.walk(self.folder_name):
            for filename in filenames:
                abs_filename = os.path.join(dirpath, filename)
                rel_path = abs_filename.split(folder_name, 1)[1]
                timestamp = os.path.getmtime(abs_filename)
                
                if os.sep == '/':
                    files[rel_path] = int(timestamp)
                else:
                    files[rel_path.replace(os.sep, '/')] = int(timestamp)
                    
        return files
    
    def run(self):
        local_files_tm = self._get_local_files()
        cloud_files_tm = self._get_cloud_files()
        
        local_files = set(local_files_tm.keys())
        cloud_files = set(cloud_files_tm.keys())
        
        def _upload(f):
            filename = join_local_path(self.folder_name, f)
            cloud_path = self._add_timestamp_to_filename(f, local_files_tm[f])
            self.storage.upload(cloud_path, filename)
            
        def _download(f):
            filename = join_local_path(self.folder_name, f)
            cloud_path = self._add_timestamp_to_filename(f, cloud_files_tm[f])
            self.storage.download(cloud_path, filename)
        
        for f in (local_files - cloud_files):
            _upload(f)
            
        for f in (cloud_files - local_files):
            _download(f)
            
        for f in (cloud_files & local_files):
            if local_files_tm[f] < cloud_files_tm[f]:
                _download(f)
            elif local_files_tm[f] > cloud_files_tm[f]:
                _upload(f)
                
        if self.loop:
            time.sleep(self.sec)
            self.run()