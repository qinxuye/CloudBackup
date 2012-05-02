#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-5-1

@author: Chine
'''

import os

from CloudBackup.lib.vdisk import VdiskClient
from CloudBackup.lib.s3 import S3Client
from CloudBackup.lib.errors import VdiskError
from CloudBackup.utils import join_path

__author__ = "Chine King"

class Storage(object):
    def _ensure_cloud_path_legal(self, cloud_path):
        return cloud_path.strip('/')
    
    def set_holder(self, holder_name):
        raise NotImplementedError
    
    def upload(self, cloud_path, filename):
        raise NotImplementedError
    
    def download(self, cloud_path, filename):
        raise NotImplementedError
    
    def list(self, cloud_path, recursive=False):
        raise NotImplementedError
    
    def list_files(self, cloud_path, recursive=False):
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
    def __init__(self, client, cache={}, holder_name=''):
        '''
        :param client: must be VdiskClient or it's subclass, CryptoVdiskClient eg.
        :param cache(optional): the cache to store key-value-pair-> path: id, blank dict as default.
        :param holder_name(optional): the folder that holder the content, blank as default.
        '''
        
        assert isinstance(client, VdiskClient)
        
        self.cache = cache
        self.client = client
        self.holder = holder_name
        
    def set_holder(self, holder_name):
        self.holder = holder_name
        
    def _ensure_cloud_path_legal(self, cloud_path):
        path = join_path(self.holder, cloud_path)
        return super(VdiskStorage, self)._ensure_cloud_path_legal(path)
        
    def _get_cloud_dir_id(self, cloud_path):
        if len(cloud_path) == 0:
            return 0
        
        dir_id = self.cache.get(cloud_path, 0)
        if dir_id != 0:
            return dir_id
        
        path = '/' + cloud_path if not cloud_path.startswith('/') else cloud_path
            
        try:
            dir_id = self.client.get_dirid_with_path(path)
            
            self.cache[cloud_path] = str(dir_id)
            return dir_id
        except VdiskError, e:
            if e.err_no == 3: # means the dir not exist
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
            dir_path, cloud_name = tuple(cloud_path.rsplit('/', 1))
            dir_id = self._get_cloud_dir_id(dir_path)
        else:
            cloud_name = cloud_path
            
        self.client.upload_file(filename, dir_id, cover, upload_name=cloud_name)
        
    def download(self, cloud_path, filename):
        '''
        Download the file to local from cloud.
        
        :param cloud_path: the path on the cloud, 'test/file.txt' eg, not need to start with '/'
        :param filename: the local file's absolute path.
        '''
        
        cloud_path = self._ensure_cloud_path_legal(cloud_path)
        
        fid = self._get_cloud_file_id(cloud_path)
        
        self.client.download_file(fid, filename)
            
    def list(self, cloud_path, recursive=False):
        '''
        list all objects include folders and files in a cloud path.
        
        :param cloud_path: the path on the cloud, 'test' eg, not need to start with '/'
                           list the root path if set to blank('').
        :param recursive(Optional): if set to True, will return the objects recursively.
        
        :return: it doesn't return all the objects immediately,
                 it returns an object each time, and then another, and goes on.
                 you shoud iterate them by for loop.
                 of course, you can use list() to put them all into memory,
                 however, it is not recommended.
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
                path = join_path(cloud_path, itm.name)
                if 'url' in itm:
                    yield CloudFile(path, itm.type, itm.md5, id=itm.id)
                else:
                    yield CloudFolder(path, id=itm.id)
                    
                    if recursive and itm.file_num + itm.dir_num > 0:
                        for obj in self.list(path, recursive):
                            yield obj
                            
    def list_files(self, cloud_path, recursive=False):
        '''
        list all the files in a cloud path.
        
        :param cloud_path: the path on the cloud, 'test' eg, not need to start with '/'
                           list the root path if set to blank('').
        :param recursive(Optional): if set to True, will return the files recursively.
        
        :return: it doesn't return all the files immediately,
                 it returns a file(a CloudFile instance) each time, and then another, and goes on.
                 you shoud iterate them by for loop.
                 of course, you can use list() to put them all into memory,
                 however, it is not recommended.
        '''
        
        for obj in self.list(cloud_path, recursive):
            if isinstance(obj, CloudFile):
                yield obj
                            
    def info(self, cloud_path):
        '''
        Get the infomation of a file on the cloud.
        
        :param cloud_path: the path on the cloud, 'test/file.txt' eg, not need to start with '/'.
        
        :return: an instance of CloudFile.
        '''
        
        cloud_path = self._ensure_cloud_path_legal(cloud_path)
        
        fid = self._get_cloud_file_id(cloud_path)
        kwargs = dict(self.client.get_file_info(fid))
        kwargs['path'] = cloud_path
        kwargs['content_type'] = kwargs.pop('type')
        return CloudFile(**kwargs)
    
class S3Storage(Storage):
    def __init__(self, client, holder_name):
        '''
        :param client: must be S3Client or it's subclass, CryptoS3Client eg.
        :param holder_name: the folder that holder the content.
        
        In Amazon S3, you can only store files into a bucket,
        which means the holder here.
        You have to define the holder with the unique name to store files.
        '''
        
        assert isinstance(client, S3Client)
        
        self.client = client
        self.holder = holder_name
        
        self._ensure_holder_exist(self.holder)
        
    def _ensure_holder_exist(self, holder_name):
        for bucket in self.client.list_buckets()[1]:
            if bucket.name == holder_name:
                return
            
        self.put_bucket(holder_name)
        
    def set_hodler(self, holder_name):
        self.holder = holder_name
        self._ensure_holder_exist(self.holder)
        
    def upload(self, cloud_path, filename):
        '''
        Upload local file to the cloud.
        
        :param cloud_path: the path on the cloud, 'test/file.txt' eg, not need to start with '/'
        :param filename: the local file's absolute path.
        '''
        
        cloud_path = self._ensure_cloud_path_legal(cloud_path)
        self.client.upload_file(filename, self.holder, cloud_path)
    
    def download(self, cloud_path, filename):
        '''
        Download the file to local from cloud.
        
        :param cloud_path: the path on the cloud, 'test/file.txt' eg, not need to start with '/'
        :param filename: the local file's absolute path.
        '''
        
        cloud_path = self._ensure_cloud_path_legal(cloud_path)
        self.client.download_file(filename, self.holder, cloud_path)
    
    def list(self, cloud_path, recursive=False):
        '''
        list all objects include folders and files in a cloud path.
        
        :param cloud_path: the path on the cloud, 'test' eg, not need to start with '/'
                           list the root path if set to blank('').
        :param recursive(Optional): if set to True, will return the objects recursively.
        
        :return: it doesn't return all the objects immediately,
                 it returns an object each time, and then another, and goes on.
                 you shoud iterate them by for loop.
                 of course, you can use list() to put them all into memory,
                 however, it is not recommended.
        '''
        
        cloud_path = self._ensure_cloud_path_legal(cloud_path)
        
        folders = []
        for obj in self.client.get_bucket(self.holder):
            name = obj.key
            
            splits = name.split('/')[:-1]
            tmp_path = ''
            for s in splits:
                tmp_path += s
                if tmp_path.startswith(cloud_path) \
                    and tmp_path != cloud_path \
                    and tmp_path not in folders:
                    
                    folders.append(tmp_path)
                    yield CloudFolder(tmp_path)
                    
                if not recursive:
                    break
                
                tmp_path += '/'
                
            if name.startswith(cloud_path):
                if not recursive and '/' in name.lstrip(cloud_path+'/'):
                    continue
                else:
                    content_type = getattr(obj, 'content_type', '')
                    md5 = obj.etag.strip('"')
                    yield CloudFile(name, content_type, md5)
            
    def list_files(self, cloud_path, recursive=False):
        '''
        list all the files in a cloud path.
        
        :param cloud_path: the path on the cloud, 'test' eg, not need to start with '/'
                           list the root path if set to blank('').
        :param recursive(Optional): if set to True, will return the files recursively.
        
        :return: it doesn't return all the files immediately,
                 it returns a file(a CloudFile instance) each time, and then another, and goes on.
                 you shoud iterate them by for loop.
                 of course, you can use list() to put them all into memory,
                 however, it is not recommended.
        '''
        
        cloud_path = self._ensure_cloud_path_legal(cloud_path)
        
        for obj in self.client.get_bucket(self.holder):
            name = obj.key
            if name.startswith(cloud_path):
                if not recursive and '/' in name.lstrip(cloud_path+'/'):
                    continue
                else:
                    content_type = getattr(obj, 'content_type', '')
                    md5 = obj.etag.strip('"')
                    yield CloudFile(name, content_type, md5)
    
    def info(self, cloud_path):
        '''
        Get the infomation of a file on the cloud.
        
        :param cloud_path: the path on the cloud, 'test/file.txt' eg, not need to start with '/'.
        
        :return: an instance of CloudFile.
        '''
        
        cloud_path = self._ensure_cloud_path_legal(cloud_path)
        
        s3_obj = self.client.get_object(self.holder, cloud_path)
        
        kwargs = {}
        for attr in dir(s3_obj):
            if not attr.startswith('_') \
                and attr != 'mapping' \
                and attr != 'from_xml':
                
                kwargs[attr] = getattr(s3_obj, attr)
                
        kwargs['md5'] = kwargs.pop('etag').strip('"')
        kwargs['path'] = cloud_path
        
        return CloudFile(**kwargs)