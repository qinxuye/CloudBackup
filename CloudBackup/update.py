'''
Created on 2012-5-9

filefolder update

@author: WangZheng
'''

from CloudBackup.cloud import VdiskStorage, S3Storage
import os
import time

class hand(object):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
    def  update(self,path,storage):
        
        if os.path.isdir(path)==False:
            pass
        
        firstpath=os.path.split(path)[0]
        lastpath=os.path.split(path)[1]
    
        print "Current File folder is",firstpath,lastpath
        
        folderdict={}
        for netfolder in storage.list(lastpath):
            folderdict.update({netfolder.path:0})
        netdict={}
        for netfile in storage.list_files(lastpath,True): 
                #print netfile.path
                folderdict[netfile.path]=1          
                if os.sep=='\\':
                    netfile.path=netfile.path.replace('/','\\')
                netmodetime=netfile.path.split('.t')[-1]
                dlfile=firstpath+netfile.path.replace('.t'+netmodetime,'')
                netdict.update({dlfile:netmodetime})

        localdict={}                
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath=os.path.join(dirpath,filename)
                lastmtime=int(os.path.getmtime(filepath))                
                localdict.update({filepath:lastmtime})
        
        nethand={}#0:nothing 1:delete 2:download
        localhand={}#0:nothing 1:delete 2:upload
        
        for netkey in netdict.keys():
            netvalue=int(round(float(netdict[netkey])))
            if localdict.has_key(netkey)==False:
                nethand.update({netkey:2})
            else:
                localvalue=int(localdict[str(netkey)])
                if  netvalue > localvalue:#net is newer than local
                    nethand.update({netkey:2})
                    localhand.update({netkey:1})
                    #print ">"
                if  netvalue < localvalue:#local is newer than net
                    nethand.update({netkey:1})
                    localhand.update({netkey:2})
                    #print "<"
                if  netvalue == localvalue:
                    nethand.update({netkey:0})
                    localhand.update({netkey:0})
                    #print "=="
                
                
        for localkey in localdict.keys():
            if  localhand.has_key(localkey)==False:
                localhand.update({localkey:2})
       
        #print nethand.keys(),nethand.values()
        #print localhand.keys(),localhand.values()
        
        for nethandkey in nethand.keys():
            uploadpath=nethandkey.replace(firstpath,'')+'.t'+netdict[nethandkey]
            if os.sep=='\\':
                uploadpath=uploadpath.replace('\\','/')
            if nethand[nethandkey]==1:    
                storage.delete(uploadpath)
                print "delete in Cloud",uploadpath
            if nethand[nethandkey]==2:
                if localhand.has_key(nethandkey) and localhand[nethandkey]==1:
                    os.remove(nethandkey)
                    print "delete",nethandkey
                print nethandkey,uploadpath
                storage.download(uploadpath,nethandkey)
            
        for localhandkey in localhand.keys():
            uploadpath=localhandkey.replace(firstpath,'')+'.t'+str(localdict[localhandkey])
            if os.sep=='\\':
                uploadpath=uploadpath.replace('\\','/')
            if localhand[localhandkey]==2:
                print "upload",localhandkey,"to",uploadpath
                storage.upload(uploadpath,str(localhandkey))
        
        
        '''
        used to delete empty folder
        '''
        print "Folder"
        for netfolder in folderdict.keys():
            if folderdict[netfolder]==0:
                print netfolder
                print [tempfile for tempfile in storage.list(netfolder)].__len__()
                if [tempfile for tempfile in storage.list(netfolder)].__len__()==0:
                    
                    storage.delete(netfolder)
                    print "delete",netfolder

        print "Update Complete in",time.ctime()
        