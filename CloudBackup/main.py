'''
Created on 2012-5-9

@author: WangZheng
'''

from CloudBackup.lib.vdisk import VdiskClient, CryptoVdiskClient
from CloudBackup.lib.s3 import S3Client
from CloudBackup.test.settings import *
from CloudBackup.cloud import VdiskStorage, S3Storage

from CloudBackup.update import hand
import os

def main():
    client = VdiskClient(VDISK_APP_KEY, VDISK_APP_SECRET)
    client.auth(VDISK_TEST_ACCOUNT, VDISK_TEST_PASSWORD)
    s = VdiskStorage(client)
    
    path=('F:\\Cloud')
    updatehand = hand()
    updatehand.update(path, s)
    '''
    if os.path.isdir(path)==False:
        pass
    firstpath=os.path.split(path)[0]
    lastpath=os.path.split(path)[1]
    
    print firstpath,lastpath
    
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            lastmtime=os.path.getmtime(os.path.join(dirpath,filename))
            filepath=os.path.join(dirpath,filename)
            print filepath
            uploadpath=filepath.replace(firstpath,'')
            tuploadpath=uploadpath+'_time_'+str(lastmtime)
            if os.sep=='\\':
                tuploadpath=tuploadpath.replace('\\','/')
            s.upload(tuploadpath,filepath)
            print tuploadpath
    for name in s.list_files('',True):
        s.delete(name.path)
        print name.path
    
    '''
    
        
    
    
if __name__ == '__main__':
    main()