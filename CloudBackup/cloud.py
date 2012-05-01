#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-5-1

@author: Chine
'''

import os

from CloudBackup.lib.vdisk import VdiskClient
from CloudBackup.lib.errors import VdiskError
from CloudBackup.utils import join_path

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
    
class CloudFile(object):
    def __init__(self, path, content_type, md5, **kwargs):
        self.path = path
        self.content_type = content_type
        self.md5 = md5
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
    
class CloudFolder(object):
    def __init__(self, path, **kwargs):
        self.path = path
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
    
class VdiskStorage(Storage):
    def __init__(self, client, cache={}):
        '''
        :param client: must be VdiskClient or it's subclass, CryptoClient eg.
        :param cache: the cache to store key-value-pair-> path: id, blank dict as default.
        '''
        
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
        else:
            dir_path, name = '', cloud_path
        
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
        '''
        Upload local file to the cloud.
        
        :param cloud_path: the path on the cloud, 'test/file.txt' eg, not need to start with '/'
        :param filename: the local file's absolute path.
        :cover(optional): set True to cover the file with the same name if exists. True as default.
        '''
        
        cloud_path = self._ensure_cloud_path_legal(cloud_path)
        
        dir_id = 0
        if '/' in cloud_path:
            dir_path = cloud_path.rsplit('/', 1)[0]
            dir_id = self._get_cloud_dir_id(dir_path)
            
        self.client.upload_file(filename, dir_id, cover)
        
    def download(self, cloud_path, filename):
        '''
        Download the file to local from cloud.
        
        :param cloud_path: the path on the cloud, 'test/file.txt' eg, not need to start with '/'
        :param filename: the local file's absolute path.
        '''
        
        cloud_path = self._ensure_cloud_path_legal(cloud_path)
        
        fid, cloud_fname = self._get_cloud_file_id(cloud_path, include_name=True)
        dirname, local_fname = os.path.split(filename)
        
        self.client.download_file(fid, dirname)
        if cloud_fname != local_fname:
            os.rename(os.path.join(dirname, cloud_fname), filename)
            
    def list(self, cloud_path, recursive=False):
        '''
        list all objects include folder and files in a cloud path.
        
        :param cloud_path: the path on the cloud, 'test' eg, not need to start with '/'
                           list the root path if set to blank('').
        :param recursive(Optional): if set to True, will return the objects recursively.
        '''
        
        cloud_path = self._ensure_cloud_path_legal(cloud_path)
        
        dir_path = '/' + cloud_path
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
                if 'url' in itm:
                    path = join_path(cloud_path, itm.name)
                    yield CloudFile(path, itm.type, itm.md5, id=itm.id)
                else:
                    path = join_path(cloud_path, itm.name)
                    yield CloudFolder(path, id=itm.id)
                    
                    if recursive and itm.file_num + itm.dir_num > 0:
                        for obj in self.list(path, recursive):
                            yield obj
                            
    def info(self, cloud_path):
        '''
        Get the infomation of a file on the cloud.
        
        :param cloud_path: the path on the cloud, 'test/file.txt' eg, not need to start with '/'.
        '''
        
        cloud_path = self._ensure_cloud_path_legal(cloud_path)
        
        fid = self._get_cloud_file_id(cloud_path)
        kwargs = dict(self.client.get_file_info(fid))
        kwargs['path'] = cloud_path
        kwargs['content_type'] = kwargs.pop('type')
        return CloudFile(**kwargs)