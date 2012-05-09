'''
Created on 2012-5-9

filefolder update

@author: WangZheng
'''

from CloudBackup.cloud import VdiskStorage, S3Storage
import os

class hand(object):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
    def  update(self,path,vdiskstorage):
        
        if os.path.isdir(path)==False:
            pass
        
        firstpath=os.path.split(path)[0]
        lastpath=os.path.split(path)[1]
    
        print firstpath,lastpath
        
        netdict={}
        
        for netfile in vdiskstorage.list_files(lastpath,True):
                
                if os.sep=='\\':
                    netfile.path=netfile.path.replace('/','\\')
                netmodetime=netfile.path.split('_time_')[-1]
                dlfile=firstpath+netfile.path.replace('_time_'+netmodetime,'')
                netdict.update({dlfile:netmodetime})
                
        print netdict.keys(),netdict.values()
        
        localdict={}
               
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath=os.path.join(dirpath,filename)
                lastmtime=int(os.path.getmtime(filepath))
                
                print filepath,lastmtime
                
                localdict.update({filepath:lastmtime})
                
                '''
                
                tuploadpath=filepath.replace(firstpath,'')+'_time_'+str(lastmtime)
                if os.sep=='\\':
                    tuploadpath=tuploadpath.replace('\\','/')
                
                vdiskstorage.upload(tuploadpath,filepath)
                print tuploadpath
        '''
        
        nethand={}#0:nothing 1:delete 2:download
        localhand={}#0:nothing 1:delete 2:upload
        
        print localdict.keys(),localdict.values()
        
        for netkey in netdict.keys():
            netvalue=int(round(float(netdict[netkey])))
            if localdict.has_key(netkey)==False:
                nethand.update({netkey:2})
            else:
                localvalue=int(localdict[str(netkey)])
                if  netvalue > localvalue:#net is newer than local
                    nethand.update({netkey:2})
                    localhand.update({netkey:1})
                    print ">"
                if  netvalue < localvalue:#local is newer than net
                    nethand.update({netkey:1})
                    localhand.update({netkey:2})
                    print "<"
                if  netvalue == localvalue:
                    nethand.update({netkey:0})
                    localhand.update({netkey:0})
                    print "=="
                
                
        for localkey in localdict.keys():
            if  localhand.has_key(localkey)==False:
                localhand.update({localkey:2})
       
        print nethand.keys(),nethand.values()
        print localhand.keys(),localhand.values()
        
        for nethandkey in nethand.keys():
            uploadpath=nethandkey.replace(firstpath,'')+'_time_'+netdict[nethandkey]
            if os.sep=='\\':
                uploadpath=uploadpath.replace('\\','/')
            if nethand[nethandkey]==1:
                vdiskstorage.delete(uploadpath)
            if nethand[nethandkey]==2:
                if localhand.has_key(nethandkey) and localhand[nethandkey]==1:
                    os.remove(nethandkey)
                print nethandkey,uploadpath
                vdiskstorage.download(uploadpath,nethandkey)
            
        for localhandkey in localhand.keys():
            uploadpath=localhandkey.replace(firstpath,'')+'_time_'+str(localdict[localhandkey])
            if os.sep=='\\':
                uploadpath=uploadpath.replace('\\','/')
            if localhand[localhandkey]==2:
                print uploadpath
                vdiskstorage.upload(uploadpath,str(localhandkey))
        '''
        for name in vdiskstorage.list_files('',True):
            vdiskstorage.delete(name.path)
            print name.path
        '''
        
        