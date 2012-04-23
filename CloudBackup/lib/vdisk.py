#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-4-18

@author: Chine
'''

import urllib, urllib2
import time
import os
try:
    import json # json is simplejson in 2.6+
except ImportError:
    import simplejson as json

from errors import VdiskError
from utils import hmac_sha256, encode_multipart
from crypto import DES

__author__ = "Chine King"
__description__ = "A client for vdisk api, site: http://vdisk.me/api/doc"

endpoint = "http://openapi.vdisk.me/"

def _call(url_params, params, headers=None, method="POST", try_times=3, try_interval=3):
    def _get_data():
        if method == "GET":
            if isinstance(params, str):
                full_params = "&".join((url_params, params))
            else:
                full_params = "&".join((url_params, urllib.urlencode(params)))
            path = "%s?%s" % (endpoint, full_params)
            resp = urllib2.urlopen(path)
            return json.loads(resp.read())
        
        # if method is POST
        path = "%s?%s" % (endpoint, url_params)
        if isinstance(params, str):
            encoded_params = params
        else:
            encoded_params = urllib.urlencode(params)
        
        if headers is not None:
            req = urllib2.Request(path, encoded_params, headers)
            resp = urllib2.urlopen(req)
        else:
            resp = urllib2.urlopen(path, encoded_params)
            
        return json.loads(resp.read())
    
    for i in range(try_times):
        try:
            return _get_data()
        except urllib2.URLError:
            time.sleep(try_interval)
            
        raise VdiskError(-1, "Can't not connect to server")

def get_signature(data, app_secret):
    data_str = '&'.join(['%s=%s' % (k, data[k]) for k in sorted(data)])
    return hmac_sha256(app_secret, data_str)

class VdiskClient(object):
    '''
    Vdisk client.
    
    You can use it by the steps below:
    client = VdiskClient('your_app_key', 'your_app_secret') # init
    client.auth('your_account', 'your_password') # auth
    client.upload_file('/from_path/file_name', 0, True) # call the vdisk api
    '''
    
    def __init__(self, app_key, app_secret):
        '''
        :param app_key: the app key of your vdisk api, the url is http://vdisk.me/api/addapp
        :param app_secret: the app secret
        '''
        
        self.app_key = app_key
        self.app_secret = app_secret
        self.dologid = 0
    
    def auth(self, account, password, app_type="local"):
        '''
        After init the VdiskClient object, you should auth with a user's account.
        :param account: the user's account
        :param password: the user's password
        :param app_type: 'local' stands for the vdisk user as default, 
                            and 'sinat' stands for the sina weibo user.
        '''
        
        self.account, self.password = account, password
        self.token = self.get_token(account, password, app_type)
        self._base_oper('a=keep', {'token': self.token}) # init dologid
        
    def _base_oper(self, url_params, params, **kwargs):
        result = _call(url_params, params, **kwargs)
        
        if result['err_code'] != 0:
            raise VdiskError(result['err_code'], result['err_msg'])
        
        self.dologid = result['dologid']
        
        return result.get('data'), result['dologdir']
    
    def get_token(self, account, password, app_type="local"):
        '''
        Get token.
        '''
        
        params = {
                  'account': account,
                  'password': password,
                  'appkey': self.app_key,
                  'time': time.time()
                  }
        params['signature'] = get_signature(params, self.app_secret)
        if app_type != 'local':
            params['app_type'] = app_type
            
        result = _call('m=auth&a=get_token', params)
        
        if result['err_code'] != 0:
            raise VdiskError(result['err_code'], result['err_msg'])
        
        return result['data']['token']
    
    def keep(self):
        '''
        Keep alive.
        '''
        
        self._base_oper('a=keep', {'token': self.token, 
                                   'dologid': self.dologid})
                                                  
    def keep_token(self):
        '''
        Keep the token.
        You have to do this operation every 10 to 15 minutes,
        or the token will expire.
        
        :return 0: the return data.
        :return 1: the dologdir.
        
        The example of return 0:
        {
            "uid":1000001
        }
        '''
        
        return self._base_oper('m=user&a=keep_token', {'token': self.token, 
                                                       'dologid': self.dologid})
        
    def upload_file(self, filename, dir_id, cover, 
                    maxsize=10, callback=None, dir_=None, 
                    encrypt=False, encrypt_func=None):
        '''
        Upload file.
        :param filename: the absolute path of a file
        :param dir_id: the id of the folder where the file upload to
        :param cover: bool viriable, True if you want to cover the file which exists
        :param maxsize(optional): the max size, 10M as default
        :param callback(optional): the redirect url, msg will be transfered if set
        :param dir_(optional): the dir of file exsits, the param dir_id will be ignored if this is set.
        
        :return 0: the return data.
        :return 1: the dologdir.
        
        The example of return 0:
        {
            "fid":"168593",
            "name":"MIME.txt",
            "uid":"62",
            "dir_id":0,
            "do_dir":"0,82914,82915,82916,82917",
            "ctime":1288781102,
            "ltime":1288781102,
            "size":40049,
            "type":"text/plain",
            "md5":"07c2e4630203b0425546091d044d608b",
            "url":"http://openapi.vdisk.me/open_file/……"
        }
        '''
        
        try:
            if os.path.getsize(filename) > maxsize * (1024 ** 2):
                raise VdiskError(-2, 'The file is larger than %dM' % maxsize)
        except os.error:
            raise VdiskError(-1, 'Can\'t access the file')
        
        fp = open(filename, 'rb')
        try:
            params = {
                      'token': self.token,
                      'dir_id': dir_id,
                      'cover': 'yes' if cover else 'no',
                      'file': fp,
                      'dologid': self.dologid
                      }
            
            if callback:
                params['callback'] = callback
            if dir_:
                params['dir'] = dir_
        
            if encrypt and encrypt_func is not None:
                params, boundary = encode_multipart(params, True, encrypt_func)
            else:
                params, boundary = encode_multipart(params)
            
            headers = {
                       'Content-Type': 'multipart/form-data; boundary=%s' % boundary
                       }
            
            return self._base_oper('m=file&a=upload_file', params, headers=headers)
        finally:
            fp.close()
            
    def download_file(self, fid, dir_, decrypt=False, decrypt_func=None):
        '''
        Download file by file id.
        :param fid: file id
        :param dir_: the directory where file downloads to
        '''
        data = self.get_file_info(fid)[0]
        url, filename = data['s3_url'], data['name']
        
        dest = os.path.join(dir_, filename)
        fp = open(dest, 'wb')
        
        try:
            resp = urllib2.urlopen(url)
            if decrypt and decrypt_func is not None:
                fp.write(decrypt_func(resp.read()))
            else:
                fp.write(resp.read())
        finally:
            fp.close()
            
    def create_dir(self, create_name, parent_id):
        '''
        :param create_name: dir name
        :param parent_id: the parent dir id, 0 as the root dir
        
        :return 0: the return data.
        :return 1: the dologdir.
        
        The example of return 0:
        {
            "dir_id":"35503",
            "name":"\u6d4b\u8bd5",
            "pid":0,
            "uid":"62",
            "ctime":1289271836,
            "ltime":1289271836
        }
        '''
        
        return self._base_oper('m=dir&a=create_dir', {
                                                      'token': self.token,
                                                      'create_name': create_name,
                                                      'parent_id': parent_id,
                                                      'dologid': self.dologid
                                                      })
        
    def delete_dir(self, dir_id):
        '''
        :param dir_id: the dir id
        
        :return 0: the return data.
        :return 1: the dologdir.
        '''
        
        return self._base_oper('m=dir&a=delete_dir', {
                                                      'token': self.token,
                                                      'dir_id': dir_id,
                                                      'dologid': self.dologid
                                                      })
        
    def rename_dir(self, dir_id, new_name):
        '''
        :param dir_id: dir id
        :param new_name: new name of the dir
        
        :return 0: the return data.
        :return 1: the dologdir.
        '''
        
        return self._base_oper('m=dir&a=rename_dir', {
                                                      'token': self.token,
                                                      'dir_id': dir_id,
                                                      'new_name': new_name,
                                                      'dologid': self.dologid
                                                      })
        
    def move_dir(self, dir_id, new_name, to_parent_id):
        '''
        :param dir_id: dir id
        :param new_name: new name of the dir
        :param to_parent_id: the parent dir id.
        
        :return 0: the return data.
        :return 1: the dologdir.
        The example of return 0:
        {
            "name":"\u79fb\u52a8\u540e\u7684\u76ee\u5f55",
            "dir_id":3929,
            "parent_id":0
        }
        '''
        
        return self._base_oper('m=dir&a=move_dir', {
                                                    'token': self.token,
                                                    'dir_id': dir_id,
                                                    'new_name': new_name,
                                                    'to_parent_id': to_parent_id,
                                                    'dologid': self.dologid
                                                    })
        
    def getlist(self, dir_id, page=1, pageSize=1024):
        '''
        Get the list of an dir.
        :param dir_id: dir id
        :param page(optional): the page, 1 as default
        :param pageSize(optional): the pageSize, 1024 as default and also if pageSize>=2 or pageSize<1024
        
        :return 0: the return data.
        :return 1: the dologdir.
        The example of return 0:
        {
            "list":[
                {
                    "id":"1190019",
                    "name":"test.php",
                    "dir_id":"0",
                    "ctime":"1294734798",
                    "ltime":"1294734798",
                    "size":"216 Bytes",
                    "type":"text\/php",
                    "md5":"0a706f2d0958838673dea185dd4290ed",
                    "sha1":"925b8e9a606ca5b3908ab3b53117e85ebcd35cd0",
                    "share":-1,
                    "byte":"216",
                    "length":"216",
                    "thumbnail":"http:\/\/……",//图片文件
                    "url":"http:\/\/……
                },
                ……
            ],
            "pageinfo":{
                "page":1,
                "pageSize":10,
                "rstotal":19,
                "pageTotal":2
            }
        }
        '''
        
        params = {'token': self.token,
                  'dir_id': dir_id,
                  'dologid': self.dologid}
        if page > 1: 
            params['page'] = page
        if 2 <= pageSize < 1024:
            params['pageSize'] = pageSize
            
        return self._base_oper('m=dir&a=getlist', params)
    
    def get_quota(self):
        '''
        Get the status of your vdisk usage.
        
        :return 0: the return data.
        :return 1: the dologdir.
        The example of return 0:
        {
            "used":"1330290823",
            "total":"4294967296"
        }
        '''
        
        return self._base_oper('m=file&a=get_quota', {'token': self.token,
                                                      'dologid': self.dologid})
        
    def get_file_info(self, fid):
        '''
        :param fid: file id
        
        :return 0: the return data.
        :return 1: the dologdir.
        The example of return 0:
        {
            "id":"219379", // 文件id
            "name":"VS2008TeamSuite90DayTrialCHSX1429243.part4.rar", 文件名
            "dir_id":"4280", // 目录id
            "ctime":"1289267775", // 创建时间
            "ltime":"1289267775", // 最后修改时间
            "size":"734003200", // 大小，单位(B)
            "type":"application\/x-rar-compressed",
            "md5":"5cdad57bc23f64e17fd64b45e3bf3308",
            "url":"http:\/\/openapi.vdisk.me\/open_file\/……", // 分享地址
            "s3_url":"http:\/\/data.vdisk.me\/1245/" // 下载地址
        }
        '''
        
        return self._base_oper('m=file&a=get_file_info', {'token': self.token,
                                                          'fid': fid,
                                                          'dologid': self.dologid})
        
    def delete_file(self, fid):
        '''
        :param fid: file id
        
        :return 0: the return data.
        :return 1: the dologdir.
        '''
        
        return self._base_oper('m=file&a=delete_file', {'token': self.token,
                                                        'fid': fid,
                                                        'dologid': self.dologid})    
        
    def copy_file(self, fid, new_name, to_dir_id):
        '''
        :param fid: file id
        :param new_name: new name of the file
        :param to_dir_id: the id of dir which file copied to
        
        :return 0: the return data.
        :return 1: the dologdir.
        The example of return 0:
        {
            "uid":"62",
            "ctime":1289287059,
            "ltime":1289287059,
             "size":"734003200",
             "type":"application\/x-rar-compressed",
             "md5":"5cdad57bc23f64e17fd64b45e3bf3308",
             "name":"\u526f\u672c.rar",
             "dir_id":3929,
             "fid":"222352",
             "url":"http:\/\/openapi.vdisk.me\/open_file\/……"
        }
        '''
        
        return self._base_oper('m=file&a=copy_file', {'token': self.token,
                                                      'fid': fid,
                                                      'new_name': new_name,
                                                      'to_dir_id': to_dir_id,
                                                      'dologid': self.dologid}) 
        
    def move_file(self, fid, new_name, to_dir_id):
        '''
        :param fid: file id
        :param new_name: new name of the file
        :param to_dir_id: the id of dir which file moved to
        
        :return 0: the return data.
        :return 1: the dologdir.
        The example of return 0:
        {
            "name":"\u79fb\u52a8\u540e.rar",
            "dir_id":3929,
            "fid":219379,
            "url":"http:\/\/openapi.vdisk.me\/ope……%A8%E5%90%8E.rar"
         }
        '''
        
        return self._base_oper('m=file&a=move_file', {'token': self.token,
                                                      'fid': fid,
                                                      'new_name': new_name,
                                                      'to_dir_id': to_dir_id,
                                                      'dologid': self.dologid}) 
        
    def rename_file(self, fid, new_name):
        '''
        :param fid: file id
        :param new_name: new name of the file
        
        :return 0: the return data.
        :return 1: the dologdir.
        '''
        
        return self._base_oper('m=file&a=rename_file', {'token': self.token,
                                                        'fid': fid,
                                                        'new_name': new_name,
                                                        'dologid': self.dologid})
        
    def get_dirid_with_path(self, path):
        '''
        Get the dir id by the path of it.
        :param path: path of the dir
        
        :return 0: the return data.
        :return 1: the dologdir.
        The example of return 0:
        {
            "id":12345
        }
        '''
        
        return self._base_oper('m=dir&a=get_dirid_with_path', {
                                                               'token': self.token,
                                                               'path': path,
                                                               'dologid': self.dologid
                                                               })
        
class CryptoVdiskClient(VdiskClient):
    '''
    Almost like VdiskClient, but supports uploading and downloading files with crypto.
    
    Usage:
    client = CryptoVdiskClient('your_app_key', 'your_app_secret') # init
    client.auth('your_account', 'your_password', '12345678') # auth, the third param's length must be 8
    client.upload_file('/from_path/file_name', 0, True) # call the vdisk api
    ''' 
        
    def auth(self, account, password, IV, app_type="local"):
        super(CryptoVdiskClient, self).auth(account, password, app_type)
        self.des = DES(IV)
        
    def upload_file(self, filename, dir_id, cover, maxsize=10, callback=None, dir_=None):
        return super(CryptoVdiskClient, self).upload_file(filename, dir_id, cover, 
                                                          maxsize, callback, dir_, 
                                                          True, self.des.encrypt)
        
    def download_file(self, fid, dir_):
        super(CryptoVdiskClient, self).download_file(fid, dir_, True, self.des.decrypt)