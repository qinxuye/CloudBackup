#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-5-1

@author: Chine
'''

import os

from CloudBackup.lib.vdisk import VdiskClient
from CloudBackup.lib.errors import VdiskError

__author__ = "Chine King"

class Storage(object):
    def _ensure_cloud_path_legal(self, cloud_path):
        return cloud_path.strip('/')
    
    def upload(self, cloud_path, filename):
        raise NotImplementedError
    
    def download(self, cloud_path, filename):
        raise NotImplementedError
    
    def list(self, cloud_path, recursive=False):
        raise NotImplementedError
    
    def info(self, cloud_path):
        raise NotImplementedError
    
class VdiskStorage(Storage):
    def __init__(self, client, cache={}):
        assert isinstance(client, VdiskClient)
        
        self.cache = cache
        self.client = client
        
    def _get_cloud_dir_id(self, cloud_path):
        dir_id = self.cache.get(cloud_path, 0)
        if dir_id != 0:
            return dir_id
        
        path = '/' + cloud_path if not cloud_path.startswith('/') else cloud_path
            
        try:
            dir_id = self.client.get_dirid_with_path(path)
            
            self.cache[cloud_path] = str(dir_id)
            return dir_id
        except VdiskError, e:
            if e.err_no == 3:
                parent_id = 0
                if '/' in cloud_path:
                    parent_path, name = tuple(cloud_path.rsplit('/', 1))
                    parent_id = self._get_cloud_dir_id(parent_path)
                else:
                    name = cloud_path
                    
                data = self.client.create_dir(name, parent_id)
                self.cache[cloud_path] = data.dir_id
                return data.dir_id
            else:
                raise e
        
    def _get_cloud_file_id(self, cloud_path, include_name=False):
        if cloud_path in self.cache:
            return self.cache[cloud_path]
        
        dir_id = 0
        if '/' in cloud_path:
            dir_path, name = tuple(cloud_path.rsplit('/', 1))
            dir_id = self._get_cloud_dir_id(dir_path)
        
        has_next = True
        c_page = 1
        while has_next:
            result = self.client.getlist(dir_id, page=c_page)
            if c_page >= result.pageinfo.pageTotal:
                has_next = False
            else:
                c_page += 1
                
            for itm in result.list:
                if itm.name == name:
                    self.cache[cloud_path] = itm.id
                    if include_name:
                        return itm.id, itm.name
                    return itm.id
                
        raise VdiskError('-1', 'File does\'t exist.')
    
    def upload(self, cloud_path, filename, cover=True):
        cloud_path = self._ensure_cloud_path_legal(cloud_path)
        
        dir_id = 0
        if '/' in cloud_path:
            dir_path = cloud_path.rsplit('/', 1)[0]
            dir_id = self._get_cloud_dir_id(dir_path)
            
        self.client.upload_file(filename, dir_id, cover)
        
    def download(self, cloud_path, filename):
        cloud_path = self._ensure_cloud_path_legal(cloud_path)
        
        fid, cloud_fname = self._get_cloud_file_id(cloud_path, include_name=True)
        dirname, local_fname = os.path.split(filename)
        
        self.client.download_file(fid, dirname)
        if cloud_fname != local_fname:
            os.rename(os.path.join(dirname, cloud_fname), filename)