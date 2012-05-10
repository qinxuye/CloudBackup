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

Created on 2012-5-12

@author: Chine
'''

from s3 import (S3Bucket, S3Object, AmazonUser, S3Request, 
                S3ACL, S3AclGrant, S3AclGrantByEmail)
from errors import S3Error, GSError
from utils import hmac_sha1, calc_md5, XML
from crypto import DES

__author__ = "Chine King"
__description__ = "A client for Google Cloud Storage api, site: https://developers.google.com/storage/"
__all__ = ['get_end_point', 'X_GOOG_ACL', 'ACL_PERMISSION',
           'GSAclGrantByUserID', 'GSAclGrantByUserEmail', 
           'GSAclGrantByGroupID', 'GSAclGrantByGroupEmail',
           'GSAclGrantByAllUsers', 'GSAclGrantByAllAuthenticatedUsers',
           'GSBucket', 'GSObject', 'GSUser', 'GSClient']

ACTION_TYPES = ('PUT', 'GET', 'DELETE', 'HEAD', 'POST')
STRING_TO_SIGN = '''%(action)s
%(content_md5)s
%(content_type)s
%(date)s
%(c_extension_headers)s%(c_resource)s'''
ACL = '''<AccessControlList>
  <Owner>
    <ID>%(owner_id)s</ID>
    <Name></Name>
  </Owner>
  <Entries>
%(grants)s
  </Entries>
</AccessControlList>'''
GRANT_BY_USER_ID = '''    <Entry>
      <Scope type="UserById">
        <ID>%(user_id)s</ID>
        <Name></Name>
      </Scope>
      <Permission>%(user_permission)s</Permission>
    </Entry>'''
GRANT_BY_USER_EMAIL = '''    <Entry>
      <Scope type="UserByEmail">
        <EmailAddress>%(user_email)s</EmailAddress>
        <Name></Name>
      </Scope>
      <Permission>%(user_permission)s</Permission>
    </Entry>'''
GRANT_BY_GROUP_ID = '''    <Entry>
      <Scope type="GroupById">
        <ID>%(group_id)s</ID>
        <Name></Name>
      </Scope>
      <Permission>%(user_permission)s</Permission>
    </Entry>'''
GRANT_BY_GROUP_EMAIL = '''    <Entry>
      <Scope type="GroupByEmail">
        <EmailAddress>%(group_email)s</EmailAddress>
      </Scope>
      <Permission>%(user_permission)s</Permission>
    </Entry>'''
GRANT_BY_GROUP_DOMAIN = '''    <Entry>
      <Scope type="GroupByDomain">
        <Domain>%(group_domain)s</Domain>
      </Scope>
      <Permission>%(user_permission)s</Permission>
    </Entry>'''
GRANT_BY_ALL_USERS = '''    <Entry>
      <Scope type="AllUsers" />
      <Permission>%(user_permission)s</Permission>
    </Entry>'''
GRANT_BY_ALL_AUTHENTICATED_USERS = '''    <Entry>
      <Scope type="AllAuthenticatedUsers" />
      <Permission>%(user_permission)s</Permission>
    </Entry>'''

end_point = "http://commondatastorage.googleapis.com"
def get_end_point(bucket_name=None, obj_name=None, http=False):
    prefix = 'http://' if http else ''
    url = '%s%scommondatastorage.googleapis.com' % (prefix, 
                                    bucket_name+'.' if bucket_name else '')
    if not obj_name:
        return url
    return url + obj_name if obj_name.startswith('/') else url + '/' + obj_name

class XGoogAcl(object):
    def __init__(self):
        for val in ('private', 'public-read', 'public-read-write', 
                    'authenticated-read', 'bucket-owner-read', 
                    'bucket-owner-full-control'):
            setattr(self, val.replace('-', '_'), val)
X_GOOG_ACL = XGoogAcl()

class AclPermission(object):
    def __init__(self):
        for val in ('FULL_CONTROL', 'WRITE', 'READ'):
            setattr(self, val.lower(), val)
ACL_PERMISSION = AclPermission()

class GSACL(S3ACL):
    '''Google Cloud Storage acl'''
    
    def __str__(self):
        return ACL % {
                  'owner_id': self.owner.id_,
                  'grants': self.grants_str
               }
    
class GSAclGrant(S3AclGrant):
    'Base Google cloud storage acl grant. refer to https://developers.google.com/storage/docs/accesscontrol'
    
    @classmethod
    def from_xml(cls, tree):
        scope = tree.find('Scope')
        scope_type = scope.attrib['type']
        permission = tree.find('Permission').text
        
        if scope_type == 'UserById':
            id_ = scope.find('ID')
            if hasattr(id_, 'text'):
                return GSAclGrantByUserID(GSUser(id_.text), permission)
        elif scope_type == 'UserByEmail':
            email = scope.find('EmailAddress')
            if hasattr(email, 'text'):
                return GSAclGrantByUserEmail(email.text, permission)
        elif scope_type == 'GroupById':
            id_ = scope.find('ID')
            if hasattr(id_, 'text'):
                return GSAclGrantByGroupID(id_.text, permission)
        elif scope_type == 'GroupByEmail':
            email = scope.find('EmailAddress')
            if hasattr(email, 'text'):
                return GSAclGrantByGroupEmail(email.text, permission)
        elif scope_type == 'GroupByDomain':
            domain = scope.find('Domain')
            if hasattr(domain, 'text'):
                return GSAclGrantByGroupDomain(domain.text, permission)
        elif scope_type == 'AllUsers':
            return GSAclGrantByAllUsers(permission)
        elif scope_type == 'AllAuthenticatedUsers':
            return GSAclGrantByAllAuthenticatedUsers(permission)
    
class GSAclGrantByUserID(GSAclGrant):
    '''
    Google cloud storage acl grant, need the user's canonical id.
    permission value can be  FULL_CONTROL | WRITE |  READ.
    '''
    
    def __init__(self, gs_user, permission):
        assert isinstance(gs_user, GSUser)
        
        self.user = gs_user
        self.permission = permission
        
    def _get_grant(self, permission):
        return GRANT_BY_USER_ID % {
                    'user_id': self.user.id_,
                    'user_permission': permission
               }
        
class GSAclGrantByUserEmail(S3AclGrantByEmail):
    '''
    Google cloud storage acl grant, need the user's email address.
    permission value can be  FULL_CONTROL | WRITE | READ
    '''
    def _get_grant(self, permission):
        return GRANT_BY_USER_EMAIL % {
                    'user_email': self.email,
                    'user_permission': permission
               }
    
class GSAclGrantByGroupID(GSAclGrant):
    '''
    Google cloud storage acl grant, need the group's id.
    permission value can be  FULL_CONTROL | WRITE | READ
    '''
    
    def __init__(self, group_id, permission):
        self.group_id = group_id
        self.permission = permission
        
    def _get_grant(self, permission):
        return GRANT_BY_GROUP_ID % {
                    'group_id': self.group_id,
                    'user_permission': permission
               }
        
class GSAclGrantByGroupEmail(GSAclGrant):
    '''
    Google cloud storage acl grant, need the group's email address.
    permission value can be  FULL_CONTROL | WRITE | READ
    '''
    
    def __init__(self, group_email, permission):
        self.group_email = group_email
        self.permission = permission
        
    def _get_grant(self, permission):
        return GRANT_BY_GROUP_EMAIL % {
                    'group_email': self.group_email,
                    'user_permission': permission
               }
        
class GSAclGrantByGroupDomain(GSAclGrant):
    '''
    Google cloud storage acl grant, need the group's email address.
    permission value can be  FULL_CONTROL | WRITE | READ
    '''
    
    def __init__(self, group_domain, permission):
        self.group_domain = group_domain
        self.permission = permission
        
    def _get_grant(self, permission):
        return GRANT_BY_GROUP_DOMAIN % {
                    'group_domain': self.group_domain,
                    'user_permission': permission
               }
        
class GSAclGrantByAllUsers(GSAclGrant):
    '''
    Google cloud storage acl grant for all users.
    permission value can be  FULL_CONTROL | WRITE | READ
    '''
    
    def __init__(self, permission):
        self.permission = permission
        
    def _get_grant(self, permission):
        return GRANT_BY_ALL_USERS % {
                    'user_permission': permission
               }
        
class GSAclGrantByAllAuthenticatedUsers(GSAclGrant):
    '''
    Google cloud storage acl grant for all users.
    permission value can be  FULL_CONTROL | WRITE | READ
    '''
    
    def __init__(self, permission):
        self.permission = permission
        
    def _get_grant(self, permission):
        return GRANT_BY_ALL_AUTHENTICATED_USERS % {
                    'user_permission': permission
               }

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
    mapping = {'id_': 'ID'}
    
    def __init__(self, id_=None, uri=None):
        self.id_ = id_
        
    def __eq__(self, other_user):
        return self.id_ == other_user.id_
            
    def __hash__(self):
        return hash(self.id_)
            
    def __str__(self):
        return self.id_
    
class GSRequest(S3Request):
    def __init__(self, access_key, secret_access_key, project_id, action, 
                 bucket_name=None, obj_name=None,
                 data=None, content_type=None, metadata={}, goog_headers={} ):
        
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
        
        self.date_str = self._get_date_str()
        
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
        else:
            headers['Content-Length'] = 0
            
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
                 canonical_user_id=None):
        self.access_key = access_key
        self.secret_key = secret_access_key
        self.project_id = project_id
        
        if canonical_user_id:
            self.owner = GSUser(canonical_user_id)
            
    def set_owner(self, owner):
        self.owner = owner
            
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
        In Google Cloud Storage, bucket's name must be unique.
        Files can be uploaded into a bucket.
        
        :return 0: owner of the bucket, instance of AmazonUser.
        :return 1: list of buckets, each one is an instance of S3Bucket.
        '''
        
        req = GSRequest(self.access_key, self.secret_key, self.project_id, 'GET')
        return req.submit(callback=self._parse_get_service)
    
    def put_bucket(self, bucket_name, x_goog_acl=X_GOOG_ACL.private, owner=None, grants=None):
        '''
        Create a bucket. if owner and grants, set bucket's acl.
        
        :param bucket_name: the name of the bucket.
        :param x_goog_acl: the acl of the bucket.
        :param owner(optional): an instance of GSUser, the owner of the bucket.
        :param *grants(optional): each of which is an instance of GSAclGrant, 
                        or its subclass: GSAclGrantByUserID, GSAclGrantByUserEmail, 
                        GSAclGrantByGroupID, GSAclGrantByGroupEmail,
                        GSAclGrantByAllUsers, GSAclGrantByAllAuthenticatedUsers.
        
        As default, x_amz_acl is private. It can be:
        private
        public-read
        public-read-write 
        authenticated-read
        bucket-owner-read 
        bucket-owner-full-control
        You can refer to the document here:
        https://developers.google.com/storage/docs/reference-headers#xgoogacl
        
        The properties of X_GOOG_ACL stand for acl list above, X_GOOG_ACL.private eg.
        But notice that the '-' must be replaced with '_', X_GOOG_ACL.public_read eg.
        '''
        
        goog_headers = {}
        if x_goog_acl != X_GOOG_ACL.private:
            goog_headers['acl'] = x_goog_acl
            
        if owner and grants:
            acl = str(GSACL(owner, *grants))
        
            req = GSRequest(self.access_key, self.secret_key, self.project_id, 'PUT',
                            bucket_name=bucket_name, obj_name='?acl', data=acl)
            return req.submit()
        
        req = GSRequest(self.access_key, self.secret_key, self.project_id, 'PUT', 
                        bucket_name=bucket_name, goog_headers=goog_headers)
        
        return req.submit()
    
    def _parse_get_acl(self, data):
        tree = XML.loads(data)
        
        owner = GSUser.from_xml(tree.find('Owner'))
        
        grants = []
        for entry in tree.find('Entries').getchildren():
            grants.append(GSAclGrant.from_xml(entry))
               
        return owner, grants
    
    def _parse_get_bucket(self, data):
        tree = XML.loads(data)
        bucket = GSBucket.from_xml(tree)
        has_next = True if bucket.is_truncated == 'true' else False
        
        objs = []
        for ele in tree.findall('Contents'):
            obj = GSObject.from_xml(ele)
            obj.bucket = bucket
            objs.append(obj)
            
        common_prefix = []
        for ele in tree.findall('CommonPrefixes'):
            prefix = ele.find('Prefix')
            if hasattr(prefix, 'text'):
                common_prefix.append(prefix.text)
            
        return objs, common_prefix, has_next
    
    def get_bucket(self, bucket_name, acl=False, **kwargs):
        '''
        If not acl, list objects in the bucket by the bucket's name.
        
        :param bucket_name
        
        :return 0: list of objects in the bucket, each one is an instance of GSObject.
        :return 1: the common prefix list, always when prefix parameter in kwargs.
        :return 2: if has next objects.
        
        Else if acl, get buckt's acl.
        
        :param bucket_name
        
        :return 0: the owner of the buckt, an instance of GSUser.
        :return 1: a list. each one is an isntance of GSAclGrant or its subclass.
                   including: GSAclGrantByUserID, GSAclGrantByUserEmail, 
                   GSAclGrantByGroupID, GSAclGrantByGroupEmail,
                   GSAclGrantByAllUsers, GSAclGrantByAllAuthenticatedUsers.
        '''
        
        if acl:
            req = GSRequest(self.access_key, self.secret_key, self.project_id, 'GET',
                            bucket_name=bucket_name, obj_name='?acl')
            return req.submit(callback=self._parse_get_acl)
        
        args = {}
        for k in ('delimiter', 'marker', 'prefix', 'max_keys'):
            v = kwargs.pop(k, None)
            if v:
                args[k] = v
        
        param = '&'.join(('%s=%s' % (k, v) for k, v in args.iteritems()))
        if not param:
            param = None
        else:
            param = '?' + param
        
        req = GSRequest(self.access_key, self.secret_key, self.project_id, 'GET',
                        bucket_name=bucket_name, obj_name=param)
        return req.submit(callback=self._parse_get_bucket)
    
    def delete_bucket(self, bucket_name):
        '''
        Delete the bucket by it's name.
        
        :param bucket_name
        '''
        
        req = GSRequest(self.access_key, self.secret_key, self.project_id, 'DELETE',
                        bucket_name=bucket_name)
        return req.submit()
    
    def get_object(self, bucket_name, obj_name, acl=False):
        '''
        Get object.
        
        :param bucket_name: the bucket contains the object.
        :param obj_name: the object's name, as the format: 'folder/file.txt' or 'file.txt'.
        :param acl: if True, return the acl infomation of the object.
        
        if acl is not True
        :return: return an instance of S3Object, the 'data' property is the content of the object.
        else
        :return 0: the owner of the buckt, an instance of GSUser.
        :return 1: a list. each one is an isntance of GSAclGrant or its subclass.
                   including: GSAclGrantByUserID, GSAclGrantByUserEmail, 
                   GSAclGrantByGroupID, GSAclGrantByGroupEmail,
                   GSAclGrantByAllUsers, GSAclGrantByAllAuthenticatedUsers.     
        '''
        
        if acl:
            req = GSRequest(self.access_key, self.secret_key, self.project_id, 'GET',
                            bucket_name=bucket_name, obj_name=obj_name+"?acl")
            return req.submit(callback=self._parse_get_acl)
        
        req = GSRequest(self.access_key, self.secret_key, self.project_id, 'GET',
                        bucket_name=bucket_name, obj_name=obj_name)
        return req.submit(include_headers=True, callback=lambda data, headers: GSObject(data=data, **headers))
    
    def put_object(self, bucket_name, obj_name, data=None, x_goog_acl=X_GOOG_ACL.private,
                   content_type=None, metadata={}, goog_headers={}, owner=None, grants=None):
        if owner and grants and not data:
            acl = str(GSACL(owner, *grants))
            
            req = GSRequest(self.access_key, self.secret_key, self.project_id, 'PUT',
                            bucket_name=bucket_name, obj_name=obj_name+'?acl', data=acl)
            return req.submit()
        
        if x_goog_acl != X_GOOG_ACL.private:
            goog_headers['acl'] = x_goog_acl
        
        req = GSRequest(self.access_key, self.secret_key, self.project_id, 'PUT',
                        bucket_name=bucket_name, obj_name=obj_name, data=data,
                        content_type=content_type, metadata=metadata, goog_headers=goog_headers)
        return req.submit()
    
    def head_object(self, bucket_name, obj_name):
        '''
        List metadata of the object.
        
        :param bucket_name: the bucket contains the object.
        :param obj_name: the object's name, as the format: 'folder/file.txt' or 'file.txt'.
        
        :return: an instance of GSObject.
        '''
        
        req = GSRequest(self.access_key, self.secret_key, self.project_id, 'HEAD',
                        bucket_name=bucket_name, obj_name=obj_name)
        return req.submit(include_headers=True, callback=lambda data, headers: S3Object(**headers))
    
    def delete_object(self, bucket_name, obj_name):
        '''
        Delete object.
        
        :param bucket_name: the bucket contains the object.
        :param obj_name: the object's name, as the format: 'folder/file.txt' or 'file.txt'.
        '''
        
        req = GSRequest(self.access_key, self.secret_key, self.project_id, 'DELETE',
                        bucket_name=bucket_name, obj_name=obj_name)
        return req.submit()
    
    def upload_file(self, filename, bucket_name, obj_name, x_goog_acl=X_GOOG_ACL.private,
                    encrypt=False, encrypt_func=None):
        '''
        Upload a local file to the Amazon S3.
        
        :param filename: the absolute path of the local file.
        :param bucket_name: name of the bucket which file puts into.
        :param obj_name: the object's name, as the format: 'folder/file.txt' or 'file.txt'.
        :param x_goog_acl: the acl of the file.
        
        As default, x_goog_acl is private. It can be:
        private
        public-read
        public-read-write 
        authenticated-read
        bucket-owner-read 
        bucket-owner-full-control
        You can refer to the document here:
        https://developers.google.com/storage/docs/reference-headers#xgoogacl
        
        The properties of X_GOOG_ACL stand for acl list above, X_GOOG_ACL.private eg.
        But notice that the '-' must be replaced with '_', X_GOOG_ACL.public_read eg.
        '''
        
        fp = open(filename, 'rb')
        try:
            goog_headers = {}
            if x_goog_acl != X_GOOG_ACL.private:
                goog_headers['acl'] = x_goog_acl
                
            data = fp.read()
            if encrypt and encrypt_func is not None:
                data = encrypt_func(data)
                
            self.put_object(bucket_name, obj_name, data=data, goog_headers=goog_headers)
        finally:
            fp.close()
            
    def download_file(self, filename, bucket_name, obj_name, 
                      decrypt=False, decrypt_func=None):
        '''
        Download the object in Google Cloud Storage to the local file.
        
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
    
class CryptoGSClient(GSClient):
    '''
    Almost like GSClient, but supports uploading and downloading files with crypto.
    
    Usage:
    # init, the third param's length must be 8
    client = CryptoS3Client('your_access_key', 'your_secret_access_key', 'your_project_id', '12345678') 
    
    # call the Google Cloud Storage api
    client.upload_file('/local_path/file_name', 'my_bucket_name', 'my_folder/file_name') 
    ''' 
    
    def __init__(self, access_key, secret_access_key, project_id, IV):
        self.IV = IV
        self.des = DES(IV)
        
        super(CryptoGSClient, self).__init__(access_key, secret_access_key, project_id)
    
    def set_crypto(self, IV):
        self.IV = IV
        self.des = DES(IV)
        
    def upload_file(self, filename, bucket_name, obj_name, x_goog_acl=X_GOOG_ACL.private, encrypt=True):
        if not hasattr(self, 'IV'):
            raise GSError(-1, msg='You haven\'t set the IV(8 length)')
        
        super(CryptoGSClient, self).upload_file(filename, bucket_name, obj_name, x_goog_acl,
                                                encrypt, self.des.encrypt)
        
    def download_file(self, filename, bucket_name, obj_name, decrypt=True):
        if not hasattr(self, 'IV'):
            raise S3Error(-1, msg='You haven\'t set the IV(8 length)')
        
        super(CryptoGSClient, self).download_file(filename, bucket_name, obj_name,
                                                  decrypt, self.des.decrypt)