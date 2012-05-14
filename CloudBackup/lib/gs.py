#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-5-12

@author: Chine
'''

from s3 import S3Bucket, S3Object, AmazonUser, S3Request
from errors import S3Error, GSError
from utils import hmac_sha1, calc_md5, XML

__author__ = "Chine King"
__description__ = "A client for Google Cloud Storage api, site: https://developers.google.com/storage/"

STRING_TO_SIGN = '''%(action)s
%(content_md5)s
%(content_type)s
%(date)s
%(c_extension_headers)s%(c_resource)s'''

end_point = "http://commondatastorage.googleapis.com"
def get_end_point(bucket_name=None, obj_name=None, http=False):
    prefix = 'http://' if http else ''
    url = '%s%scommondatastorage.googleapis.com' % (prefix, 
                                    bucket_name+'.' if bucket_name else '')
    if not obj_name:
        return url
    return url + obj_name if obj_name.startswith('/') else url + '/' + obj_name

class GSBucket(S3Bucket):
    '''
    Bucket of Google cloud storage, almost like Amazon S3 bucket.
    '''
    
class GSObject(S3Object):
    '''
    Object of Google cloud storage, almost like Amazon S3 object.
    '''
    
class GSUser(AmazonUser):
    '''
    The Google cloud storage user.
    '''
    mapping = {'id_': 'ID',
               'uri': 'URI'}
    
class GSRequest(S3Request):
    def __init__(self, access_key, secret_access_key, project_id, action, 
                 bucket_name=None, obj_name=None,
                 data=None, content_type=None, metadata={}, goog_headers={} ):
        
        super(GSRequest, self).__init__(access_key, secret_access_key, 
                 action, bucket_name=bucket_name, obj_name=obj_name,
                 data=data, content_type=content_type, metadata=metadata)
        del self.amz_headers
        
        self.project_id = project_id
        self.goog_headers = goog_headers
        self.host = get_end_point(self.bucket_name)
        self.end_point = get_end_point(self.bucket_name, self.obj_name, True)
    
    def _get_canoicalized_extension_headers(self, headers):
        goog_headers = [(k.lower(), v) for k, v in headers.iteritems() 
                       if k.lower().startswith('x-goog-')]
        goog_headers.sort()
        return '\n'.join(['%s:%s' % (k, v) for k, v in goog_headers])
    
    def _get_authorization(self, headers):
        params = {
                    'action': self.action,
                    'content_md5': headers.get('Content-MD5', ''),
                    'content_type': headers.get('Content-Type', ''),
                    'date': self.date_str,
                    'c_extension_headers': self._get_canoicalized_extension_headers(headers),
                    'c_resource': self._get_canonicalized_resource()
                 }
        if params['c_extension_headers'] and params['c_resource']:
            params['c_extension_headers'] = params['c_extension_headers'] + '\n'
        
        string_to_sign = STRING_TO_SIGN % params
        signature = hmac_sha1(self.secret_key, string_to_sign)
        
        return "GOOG1 %s:%s" % (self.access_key, signature)
    
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
            headers['x-goog-meta-' + k] = v
        for k, v in self.goog_headers.iteritems():
            headers['x-goog-' + k] = v
            
        headers['x-goog-api-version'] = 1
        headers['x-goog-project-id'] = self.project_id
        headers['Authorization'] = self._get_authorization(headers)
        
        return headers
    
    def submit(self, try_times=3, try_interval=3, callback=None, include_headers=False):
        try:
            return super(GSRequest, self).submit(
                try_times=try_times, try_interval=try_times, 
                callback=callback, include_headers=include_headers)
        except S3Error, e:
            raise GSError(e.err_no, e.tree)
    
class GSClient(object):
    '''
    Google Cloud Storage client.
    
    You can use it by the steps below:
    client = GSClient('your_access_key', 'your_secret_access_key', 'your_project_id') # init
    client.upload_file('/local_path/file_name', 'my_bucket_name', 'my_folder/file_name') 
    # call the Google Cloud Storage api
    '''
    
    def __init__(self, access_key, secret_access_key, project_id,
                 canonical_user_id=None, user_display_name=None):
        self.access_key = access_key
        self.secret_key = secret_access_key
        self.project_id = project_id
        
        if canonical_user_id and user_display_name:
            self.owner = GSUser(canonical_user_id, user_display_name)
            
    def _parse_get_service(self, data):
        tree = XML.loads(data)
        owner = GSUser.from_xml(tree.find('Owner'))
        
        buckets = []
        for ele in tree.find('Buckets').getchildren():
            buckets.append(GSBucket.from_xml(ele))
            
        return owner, buckets
        
    def get_service(self):
        '''
        List all the buckets.
        In Amazon S3, bucket's name must be unique.
        Files can be uploaded into a bucket.
        
        :return 0: owner of the bucket, instance of AmazonUser.
        :return 1: list of buckets, each one is an instance of S3Bucket.
        '''
        
        req = GSRequest(self.access_key, self.secret_key, self.project_id, 'GET')
        return req.submit(callback=self._parse_get_service)
    
    