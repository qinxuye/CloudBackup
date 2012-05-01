#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-4-20

@author: Chine
'''

import datetime
import urllib2
import time
import mimetypes

from errors import S3Error
from utils import XML, hmac_sha1, calc_md5
from crypto import DES

__author__ = "Chine King"
__description__ = "A client for Amazon S3 api, site: http://aws.amazon.com/documentation/s3/"
__all__ = ['X_AMZ_ACL', 'REGION', 'S3Bucket', 'S3Object', 'AmazonUser', 'S3Client', 'CryptoS3Client']

ACTION_TYPES = ('PUT', 'GET', 'DELETE')
GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
STRING_TO_SIGN = '''%(action)s
%(content_md5)s
%(content_type)s
%(date)s
%(c_amz_headers)s%(c_resource)s'''

end_point = "http://s3.amazonaws.com"
def get_end_point(bucket_name=None, obj_name=None, http=False):
    prefix = 'http://' if http else ''
    url = '%s%ss3.amazonaws.com' % (prefix, 
                                    bucket_name+'.' if bucket_name else '')
    if not obj_name:
        return url
    return url + obj_name if obj_name.startswith('/') else url + '/' + obj_name

class XAmzAcl(object):
    def __init__(self):
        for val in ('private', 'public-read', 'public-read-write', 
                    'authenticated-read', 'bucket-owner-read', 
                    'bucket-owner-full-control'):
            setattr(self, val.replace('-', '_'), val)
X_AMZ_ACL = XAmzAcl()

class Region(object):
    def __init__(self):
        for val in ('EU', 'eu-west-1', 'us-west-1', 'us-west-2', 
                    'ap-southeast-1', 'ap-northeast-1', 'sa-east-1'):
            setattr(self, val.replace('-', '_'), val)
        self.standard = ''
REGION = Region()
region_content = '''<CreateBucketConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/"> 
  <LocationConstraint>%s</LocationConstraint> 
</CreateBucketConfiguration >'''

class S3Base(object):
    def __init__(self, **kwargs):
        if len(kwargs) > 0 and hasattr(self, 'mapping'):
            reversed_mapping = {}
            for k, v in self.mapping.iteritems():
                reversed_mapping[v.lower()] = k
            
            for k, v in kwargs.iteritems():
                if k in reversed_mapping:
                    setattr(self, reversed_mapping[k], v)                    

class S3Bucket(S3Base):
    mapping = {'name': 'Name',
               'create_date': 'CreationDate',
               'prefix': 'Prefix',
               'marker': 'Marker',
               'max_keys': 'MaxKeys',
               'is_truncated': 'IsTruncated'}
    
    @classmethod    
    def from_xml(cls, tree):
        bucket = S3Bucket()
        
        for k, v in cls.mapping.iteritems():
            tag = tree.find(v)
            if hasattr(tag, 'text'):
                setattr(bucket, k, tag.text)
                
        return bucket
        

class S3Object(S3Base):
    mapping = {'key': 'Key',
               'last_modified': 'LastModified',
               'etag': 'ETag',
               'size': 'Size',
               'storage_class': 'StorageClass',
               'is_truncated': 'IsTruncated',
               'date': 'Date',
               'content_length': 'Content-Length',
               'content_type': 'Content-Type'}
    
    def __init__(self, **kwargs):
        if 'data' in kwargs:
            self.data = kwargs.pop('data')
        super(S3Object, self).__init__(**kwargs)
    
    @classmethod    
    def from_xml(cls, tree):
        obj = S3Object()
        
        for k, v in cls.mapping.iteritems():
            tag = tree.find(v)
            if hasattr(tag, 'text'):
                setattr(obj, k, tag.text)
                
        owner = tree.find('Owner')
        if owner is not None:
            obj.owner = AmazonUser.from_xml(owner)
                
        return obj

class AmazonUser(object):
    mapping = {'id_': 'ID',
               'display_name': 'DisplayName'}
    
    def __init__(self, id_=None, display_name=None):
        self.id_ = id_
        self.display_name = display_name
        
    @classmethod
    def from_xml(cls, tree):
        user = AmazonUser()
        
        for k, v in cls.mapping.iteritems():
            tag = tree.find(v)
            if hasattr(tag, 'text'):
                setattr(user, k, tag.text)
                
        return user

class S3Request(object):
    def __init__(self, access_key, secret_access_key, 
                 action, bucket_name=None, obj_name=None,
                 data=None, content_type=None, metadata={}, amz_headers={} ):
        
        assert action in ACTION_TYPES # action must be PUT, GET and DELETE.
        
        self.access_key = access_key
        self.secret_key = secret_access_key
        self.action = action
        
        self.bucket_name = bucket_name
        self.obj_name = obj_name
        self.data = data
        
        self.content_type = content_type
        self._set_content_type()
        
        self.metadata = metadata
        self.amz_headers = amz_headers
        
        self.date_str = self._get_date_str()
        
        self.host = get_end_point(self.bucket_name)
        self.end_point = get_end_point(self.bucket_name, self.obj_name, True)
            
    def _get_date_str(self):
        return datetime.datetime.utcnow().strftime(GMT_FORMAT)
    
    def _set_content_type(self):
        if self.obj_name is not None and not self.content_type:
            self.content_type = mimetypes.guess_type(self.obj_name)[0]
            if self.data and self.content_type is None:
                self.content_type = 'application/x-www-form-urlencoded'
            
    def _get_canonicalized_resource(self):
        path = '/'
        if self.bucket_name:
            path += self.bucket_name
        if self.bucket_name and self.obj_name:
            if not self.obj_name.startswith('/'):
                path += '/'
            path += self.obj_name
        elif self.bucket_name and not path.endswith('/'):
            path += '/'
            
        return path
    
    def _get_canoicalized_amz_headers(self, headers):
        amz_headers = [(k.lower(), v) for k, v in headers.iteritems() 
                       if k.lower().startswith('x-amz-')]
        amz_headers.sort()
        return ''.join(['%s:%s' % (k, v) for k, v in amz_headers])
    
    def _get_authorization(self, headers):
        params = {
                    'action': self.action,
                    'content_md5': headers.get('Content-MD5', ''),
                    'content_type': headers.get('Content-Type', ''),
                    'date': self.date_str,
                    'c_amz_headers': self._get_canoicalized_amz_headers(headers),
                    'c_resource': self._get_canonicalized_resource()
                 }
        if params['c_amz_headers'] and params['c_resource']:
            params['c_amz_headers'] = params['c_amz_headers'] + '\n'
        
        string_to_sign = STRING_TO_SIGN % params
        signature = hmac_sha1(self.secret_key, string_to_sign)
        
        return "AWS %s:%s" % (self.access_key, signature)
    
    def get_headers(self):
        headers = { 
                   'Date': self.date_str
                   }
        if self.data:
            headers['Content-Length'] = len(self.data)
            headers['Content-MD5'] = calc_md5(self.data)
            
        if self.content_type is not None:
            headers['Content-Type'] = self.content_type
            
        if self.bucket_name:
            headers['Host'] = self.host
        
        for k, v in self.metadata.iteritems():
            headers['x-amz-meta-' + k] = v
        for k, v in self.amz_headers.iteritems():
            headers['x-amz-' + k] = v
            
        headers['Authorization'] = self._get_authorization(headers)
        return headers
    
    def submit(self, try_times=3, try_interval=3, callback=None, include_headers=False):
        def _get_data():
            headers = self.get_headers()
            try:
                opener = urllib2.build_opener(urllib2.HTTPHandler)
                req = urllib2.Request(self.end_point, data=self.data, headers=headers)
                req.get_method = lambda: self.action
                resp = opener.open(req)
                
                if include_headers:
                    return resp.read(), resp.headers.dict
                return resp.read()
            except urllib2.HTTPError, e:
                tree = XML.loads(e.read())
                raise S3Error(tree, e.code)
            
        for i in range(try_times):
            try:
                if include_headers and callback:
                    data, headers = _get_data()
                    return callback(data, headers)
                if callback:
                    return callback(_get_data())
                return _get_data()
            except urllib2.URLError:
                time.sleep(try_interval)

class S3Client(object):
    '''
    Amazon S3 client.
    
    You can use it by the steps below:
    client = S3Client('your_access_key', 'your_secret_access_key') # init
    client.upload_file('/local_path/file_name', 'my_bucket_name', 'my_folder/file_name') 
    # call the Amazon S3 api
    '''
    
    def __init__(self, access_key, secret_access_key):
        self.access_key = access_key
        self.secret_key = secret_access_key
        
    def _parse_list_buckets(self, data):
        tree = XML.loads(data)
        owner = AmazonUser.from_xml(tree.find('Owner'))
        
        buckets = []
        for ele in tree.find('Buckets').getchildren():
            buckets.append(S3Bucket.from_xml(ele))
            
        return owner, buckets
        
    def list_buckets(self):
        '''
        List all the buckets.
        In Amazon S3, bucket's name must be unique.
        Files can be uploaded into a bucket.
        
        :return 0: owner of the bucket, instance of AmazonUser.
        :return 1: list of buckets, each one is an instance of S3Bucket.
        '''
        
        req = S3Request(self.access_key, self.secret_key, 'GET')
        return req.submit(callback=self._parse_list_buckets)
    
    def put_bucket(self, bucket_name, x_amz_acl=X_AMZ_ACL.private, region=REGION.standard):
        '''
        Create a bucket.
        
        :param bucket_name: the name of the bucket.
        :param x_amz_acl: the acl of the bucket.
        :param region: the region of the buckt puts to.
        
        As default, x_amz_acl is private. It can be:
        private
        public-read
        public-read-write 
        authenticated-read
        bucket-owner-read 
        bucket-owner-full-control
        You can refer to the document here:
        http://docs.amazonwebservices.com/AmazonS3/latest/API/RESTBucketPUT.html
        
        The properties of X_AMZ_ACL stand for acl list above, X_AMZ_ACL.private eg.
        But notice that the '-' must be replaced with '_', X_AMZ_ACL.public_read eg.
        
        The region means which data center of amazon around the world the bucket puts into,
        It can be:
        EU
        eu-west-1
        us-west-1
        us-west-2
        ap-southeast-1: Singapore
        ap-northeast-1: Tokyo
        sa-east-1
        empty string (for the US Classic Region)
        
        As the const X_AMZ_ACL, REGION's properties contain the regions list above. REGION.EU eg.
        Notice again, '-' must be replaced with '_', such as REGION.ap_southeast_1.
        
        As tokyo's data center is nearest to us, REGION.ap_northeast_1 is strongly recommended.
        '''
        
        amz_headers = {}
        if x_amz_acl != X_AMZ_ACL.private:
            amz_headers['acl'] = x_amz_acl
            
        if region != REGION.standard:
            data = region_content % region
        else:
            data = None
        
        req = S3Request(self.access_key, self.secret_key, 'PUT', 
                        bucket_name=bucket_name, data=data, amz_headers=amz_headers)
        
        return req.submit()
    
    def _parse_get_bucket(self, data):
        tree = XML.loads(data)
        bucket = S3Bucket.from_xml(tree)
        
        objs = []
        for ele in tree.findall('Contents'):
            obj = S3Object.from_xml(ele)
            obj.bucket = bucket
            objs.append(obj)
            
        return objs
    
    def get_bucket(self, bucket_name):
        '''
        List objects in the bucket by the bucket's name.
        
        :param bucket_name
        
        :return: list of objects in the bucket, each one is an instance of S3Object.
        '''
        
        req = S3Request(self.access_key, self.secret_key, 'GET',
                        bucket_name=bucket_name)
        return req.submit(callback=self._parse_get_bucket)
    
    def delete_bucket(self, bucket_name):
        '''
        Delete the bucket by it's name.
        
        :param bucket_name
        '''
        
        req = S3Request(self.access_key, self.secret_key, 'DELETE',
                        bucket_name=bucket_name)
        return req.submit()
    
    def put_object(self, bucket_name, obj_name, data, content_type=None, 
                   metadata={}, amz_headers={}):
        '''
        Put object into a bucket.
        
        :param bucket_name: which bucket the object puts into.
        :param obj_name: the obj name, as the format: 'folder/file.txt' or 'file.txt'.
        :param data: the content of the obj.
        :param content_type
        :param metadata: the meta data as amazon defined.
        :param amz_header: the extra headers which amazon defined.
        
        In Amazon S3, you can't simply create a folder. 
        Actually, when you upload file with the obj_name 'myfolder/myfile.txt',
        S3 will create a folder named 'myfolder' automatically, 
        and then put the object(file here) into the folder,
        so you don't need to worry about it.
        
        This method is a low-level api, 
        the method 'upload_file' is recommended as the high-level api.
        '''
        
        req = S3Request(self.access_key, self.secret_key, 'PUT',
                        bucket_name=bucket_name, obj_name=obj_name, data=data,
                        content_type=content_type, metadata=metadata, amz_headers=amz_headers)
        return req.submit()
    
    def get_object(self, bucket_name, obj_name):
        '''
        Get object.
        
        :param bucket_name: the bucket contains the object.
        :param obj_name: the object's name, as the format: 'folder/file.txt' or 'file.txt'.
        
        :return: instance of S3Object, the 'data' property is the content of the object.
        '''
        
        req = S3Request(self.access_key, self.secret_key, 'GET',
                        bucket_name=bucket_name, obj_name=obj_name)
        return req.submit(include_headers=True, callback=lambda data, headers: S3Object(data=data, **headers))
    
    def delete_object(self, bucket_name, obj_name):
        '''
        Delete object.
        
        :param bucket_name: the bucket contains the object.
        :param obj_name: the object's name, as the format: 'folder/file.txt' or 'file.txt'.
        '''
        
        req = S3Request(self.access_key, self.secret_key, 'DELETE',
                        bucket_name=bucket_name, obj_name=obj_name)
        return req.submit()
    
    def upload_file(self, filename, bucket_name, obj_name, x_amz_acl=X_AMZ_ACL.private,
                    encrypt=False, encrypt_func=None):
        '''
        Upload a local file to the Amazon S3.
        
        :param filename: the absolute path of the local file.
        :param bucket_name: name of the bucket which file puts into.
        :param obj_name: the object's name, as the format: 'folder/file.txt' or 'file.txt'.
        :param x_amz_acl: the acl of the file.
        
        As default, x_amz_acl is private. It can be:
        private
        public-read
        public-read-write 
        authenticated-read
        bucket-owner-read 
        bucket-owner-full-control
        You can refer to the document here:
        http://docs.amazonwebservices.com/AmazonS3/latest/API/RESTBucketPUT.html
        
        The properties of X_AMZ_ACL stand for acl list above, X_AMZ_ACL.private eg.
        But notice that the '-' must be replaced with '_', X_AMZ_ACL.public_read eg.
        '''
        
        fp = open(filename, 'rb')
        try:
            amz_headers = {}
            if x_amz_acl != X_AMZ_ACL.private:
                amz_headers['acl'] = x_amz_acl
                
            data = fp.read()
            if encrypt and encrypt_func is not None:
                data = encrypt_func(data)
                
            self.put_object(bucket_name, obj_name, data, amz_headers=amz_headers)
        finally:
            fp.close()
            
    def download_file(self, filename, bucket_name, obj_name, 
                      decrypt=False, decrypt_func=None):
        '''
        Download the object in Amazon S3 to the local file.
        
        :param filename: the absolute path of the local file.
        :param bucket_name: name of the bucket which file puts into.
        :param obj_name: the object's name, as the format: 'folder/file.txt' or 'file.txt'.
        '''
        
        fp = open(filename, 'wb')
        try:
            data = self.get_object(bucket_name, obj_name).data
            
            if decrypt and decrypt_func is not None:
                data = decrypt_func(data)
            
            fp.write(data)
        finally:
            fp.close()
            
class CryptoS3Client(S3Client):
    '''
    Almost like S3Client, but supports uploading and downloading files with crypto.
    
    Usage:
    # init, the third param's length must be 8
    client = CryptoS3Client('your_access_key', 'your_secret_access_key', 12345678') 
    
    # call the Amazon S3 api
    client.upload_file('/local_path/file_name', 'my_bucket_name', 'my_folder/file_name') 
    ''' 
    
    def __init__(self, access_key, secret_access_key, IV):
        self.IV = IV
        self.des = DES(IV)
        
        super(CryptoS3Client, self).__init__(access_key, secret_access_key)
    
    def set_crypto(self, IV):
        self.IV = IV
        self.des = DES(IV)
        
    def upload_file(self, filename, bucket_name, obj_name, x_amz_acl=X_AMZ_ACL.private, encrypt=True):
        if not hasattr(self, 'IV'):
            raise S3Error(None, -1, 'You haven\'t set the IV(8 length)')
        
        super(CryptoS3Client, self).upload_file(filename, bucket_name, obj_name, x_amz_acl,
                                                encrypt, self.des.encrypt)
        
    def download_file(self, filename, bucket_name, obj_name, decrypt=True):
        if not hasattr(self, 'IV'):
            raise S3Error(None, -1, 'You haven\'t set the IV(8 length)')
        
        super(CryptoS3Client, self).download_file(filename, bucket_name, obj_name,
                                                  decrypt, self.des.decrypt)