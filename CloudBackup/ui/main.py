#!/usr/bin/env python
#coding=utf-8

'''
Created on 2012-5-9

@author: zhao yuan
'''

import sys
from PyQt4 import QtCore ,QtGui

from CloudBackup.environment import Environment
from CloudBackup.lib.errors import VdiskError, S3Error, GSError
from CloudBackup.cloud import CloudFile
from CloudBackup.cloud import CloudFolder
import CloudBackup.mail

import CloudBackup_UI
import VDiskLogin_UI
import VDiskShare_UI
import S3Login_UI
import S3Share_UI
import GoogleCloudLogin_UI
import GoogleCloudShare_UI



try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class Start(QtGui.QMainWindow):

    def __init__(self,parent = None):
        QtGui.QWidget.__init__(self,parent)       
        self.ui = CloudBackup_UI.Ui_CloudBackupUI()
        self.ui.setupUi(self)
        
        self.env = Environment()
        
        vdisk_info = self.env.load_vdisk_info()
        if vdisk_info is None:
            self.vuserstate = False
        else:
            self.vuserstate = True
            self.ui.tvdirpath.setText(
                QtCore.QString(vdisk_info['local_folder'].decode('utf-8')))
            self.vdisk_setup(vdisk_info['account'], vdisk_info['password'])
            self.ui.button_v_submit.setText(QtCore.QString(u'正在同步...'))
            self.vdisk_set_userstate(vdisk_info['account'])
            
        self.suserstate = False
        self.guserstate = False
        
        # register the button function under the VDisk syn file-dir
        QtCore.QObject.connect(self.ui.button_v_dir, QtCore.SIGNAL("clicked()"),
                               self.vdisk_syn_dir)
        
        if not self.vuserstate:
            QtCore.QObject.connect(self.ui.button_v_submit, QtCore.SIGNAL("clicked()"),
                                   self.vdisk_dir_submit)
        
        QtCore.QObject.connect(self.ui.button_v_reset, QtCore.SIGNAL("clicked()"),
                               self.vdisk_dir_reset)
        
        QtCore.QObject.connect(self.ui.button_v_share, QtCore.SIGNAL("clicked()"),
                               self.vdisk_file_share)
        
        QtCore.QObject.connect(self.ui.button_v_logflush, QtCore.SIGNAL("clicked()"),
                               self.vdisk_log_flush)
        
        # register the button function under the S3 syn file-dir
        QtCore.QObject.connect(self.ui.button_s_dir, QtCore.SIGNAL("clicked()"),
                               self.s3_syn_dir)
        
        QtCore.QObject.connect(self.ui.button_s_submit, QtCore.SIGNAL("clicked()"),
                               self.s3_dir_submit)
        
        QtCore.QObject.connect(self.ui.button_s_reset, QtCore.SIGNAL("clicked()"),
                               self.s3_dir_reset)
        
        QtCore.QObject.connect(self.ui.button_s_share, QtCore.SIGNAL("clicked()"),
                               self.s3_file_share)
        
        QtCore.QObject.connect(self.ui.button_s_logflush, QtCore.SIGNAL("clicked()"),
                               self.s3_log_flush)
        
        
        # register the button function under the googlecloud syn file-dir
        QtCore.QObject.connect(self.ui.button_g_dir, QtCore.SIGNAL("clicked()"),
                               self.gs_syn_dir)
        
        QtCore.QObject.connect(self.ui.button_g_submit, QtCore.SIGNAL("clicked()"),
                               self.gs_dir_submit)
        
        QtCore.QObject.connect(self.ui.button_g_reset, QtCore.SIGNAL("clicked()"),
                               self.gs_dir_reset)
        
        QtCore.QObject.connect(self.ui.button_g_share, QtCore.SIGNAL("clicked()"),
                               self.gs_file_share)
        
        QtCore.QObject.connect(self.ui.button_g_logflush, QtCore.SIGNAL("clicked()"),
                               self.gs_log_flush)
    
    def closeEvent(self, event): 
        self.env.stop_vdisk(clear_info=False)
        event.accept()    
        
    def alert(self, msg):
        if isinstance(msg, str):
            msg = msg.decode('utf-8')
        
        errorbox = QtGui.QMessageBox()
        errorbox.setText(QtCore.QString(msg))
        errorbox.setWindowTitle(QtCore.QString(u"错误！"))
        errorbox.exec_()
        
    def vdisk_reset_init_state(self):
        self.ui.button_v_submit.setText(QtCore.QString(u'开始同步'))
        QtCore.QObject.connect(self.ui.button_v_submit, QtCore.SIGNAL("clicked()"),
                               self.vdisk_dir_submit)
        self.ui.lvuserstate.setText(QtCore.QString(u'用户登录状态'))
            
    def file_dir(self):
        """
        provide a dialog for the user to get the folder
        """  
        
        fd = QtGui.QFileDialog(self)
        filedir = fd.getExistingDirectory(parent=None, caption="File Dir")
                
        return filedir
    
    def get_cloud_path(self,tree):
        '''
        get the cloud path of the selected file
        '''
        
        items = tree.selectedItems()
        try:
            path = items[0].toolTip(0)  
            path = str(path)       
            return path
        except IndexError,e:
            mbox = QtGui.QMessageBox()
            mbox.setText("Choose a File to be shared!")
            mbox.setWindowTitle("Hint")
            mbox.exec_()
            return None
    
    def vdisk_syn_dir(self):
        """
        select a syn folder
        """
        
        filedir = self.file_dir()
        self.ui.tvdirpath.setText(filedir)
        
    def vdisk_dir_reset(self):
        """
        stop the current syn folder , clear all the associated info
        """
        
        self.ui.tvdirpath.clear()
        self.ui.VtreeWidget.clear()
        self.ui.VlogTreeWidget.clear() 
        self.env.stop_vdisk()
        self.vdisk_reset_init_state()
        self.vuserstate = False
        
    def vdisk_dir_submit(self):
        """
        submit the cloud info so that the selected folder become the syn folder
        """
        
        if len(self.ui.tvdirpath.text()) == 0:
            self.alert(u"同步文件夹不能为空！")
            return
        
        if self.vuserstate == False:
           
            self.vlogin = QtGui.QDialog()
            self.vlogin.ui = VDiskLogin_UI.Ui_VDiskCloudLoginUI()
            self.vlogin.ui.setupUi(self.vlogin)
            self.ui.button_v_submit.setText(QtCore.QString(u'正在同步...'))
            
            QtCore.QObject.connect(self.vlogin.ui.button_submit, QtCore.SIGNAL("clicked()"),
                               self.vdisk_login_submit)
            QtCore.QObject.connect(self.vlogin.ui.button_reset, QtCore.SIGNAL("clicked()"),
                               self.vdisk_login_reset)
            
            
            self.vlogin.exec_()
        else:
            #self.vdisk_dir_reset()
            self.vdisk_setup(self.vdisk_user,self.vdisk_pwd)
            
    def vdisk_login_submit(self):
        """
        submit the cloud info to the cloud , show the files and the logs that  synchronized with the cloud
        """
        
        user = self.vlogin.ui.tvuser.text()
        pwd = self.vlogin.ui.tvpwd.text()
        self.vdisk_user = user
        self.vdisk_pwd = pwd
        
        self.vdisk_setup(user, pwd)
        self.vdisk_set_userstate(user)
               
        self.vlogin.close()
        
    def vdisk_set_userstate(self, user):
        self.ui.lvuserstate.setText(
            QtCore.QString(("Hello, 微盘用户 %s" % user).decode('utf-8')))
        
        
    def vdisk_setup(self,user,pwd):     
        """
        use the info of the cloud submitted to setup the cloud storage syn folder 
        """
        
        try:
            if len(self.ui.tvdirpath.text()) == 0:
                self.alert(u"同步文件夹不能为空！")
                return
            
            self.vdisk_handler = self.env.setup_vdisk(str(user),str(pwd),str(self.ui.tvdirpath.text()),'cldbkp_'+str(user))
            self.vuserstate = True      
            
            self.ui.VtreeWidget.clear()
            value = QtCore.QString(QtGui.QApplication.translate("Directory", "根目录", None, QtGui.QApplication.UnicodeUTF8))
            stringlist = QtCore.QStringList(value)
            root = QtGui.QTreeWidgetItem(stringlist)
            self.ui.VtreeWidget.addTopLevelItem(root)
            
            self.vdisk_show_files(par = root)       
            self.vdisk_show_logs()
            
    
        except VdiskError, e:
            
            message = e.msg
            errorbox = QtGui.QMessageBox()
            errorbox.setText("Login Failed")
            errorbox.setWindowTitle("Error")
            errorbox.setInformativeText(message)
            errorbox.exec_()

    
    def vdisk_show_files(self,path = '',par = None):
        """
        show the files that  synchronized with the cloud
        """
        
        if self.vdisk_handler != None :
            
            for theone in self.vdisk_handler.list_cloud(path):
                
                if theone is None: return
                
                if isinstance(theone, CloudFile):
                    filename = theone.path.split('/')[-1]
                    value = QtCore.QString(filename.decode('utf-8'))
                    stringlist = QtCore.QStringList(value)
                    thefile =  QtGui.QTreeWidgetItem(stringlist)  
                    thefile.setToolTip(0,QtCore.QString(theone.cloud_path))            
                    par.addChild(thefile)
                        
                elif isinstance(theone, CloudFolder):
                    foldername = theone.path.split('/')[-1]
                    value = QtCore.QString(foldername.decode('utf-8'))
                    stringlist = QtCore.QStringList(value)
                    folder =  QtGui.QTreeWidgetItem(stringlist)
                    par.addChild(folder)
                    self.vdisk_show_files(foldername,folder)              
                    
    def vdisk_show_logs(self):
        """
        show the logs about files that synchronized with the cloud
        """
        
        self.ui.VlogTreeWidget.clear()
        
        for log in self.vdisk_handler.log_obj.get_logs():
            
            if log is None: return
            
            splits = log.split(' ', 2)
            
            if len(splits) == 3:
                stime = ' '.join((splits[i] for i in range(2)))
                saction = splits[2]
                
                log =  QtGui.QTreeWidgetItem()
                log.setText(0, QtCore.QString(stime))
                log.setText(1, QtCore.QString(saction.decode('utf-8')))
            
            self.ui.VlogTreeWidget.addTopLevelItem(log)
    
    def vdisk_login_reset(self):
        """
        clear the info about the account in the cloud
        """
        self.vlogin.ui.tvpwd.clear()
        self.vlogin.ui.tvuser.clear()
        
        
    def vdisk_file_share(self):
        """
        share a syn file to others by email
        """
        
        self.vdisk_file_path = self.get_cloud_path(self.ui.VtreeWidget)
        
        if self.vdisk_file_path is None: return
        
        self.vshare = QtGui.QDialog()
        self.vshare.ui = VDiskShare_UI.Ui_Vdisk_Share()
        self.vshare.ui.setupUi(self.vshare)
        
        self.vshare.ui.tvrec.setToolTip(QtCore.QString("split the addresses with ',' "))
        
        storage = self.vdisk_handler.storage
        sharepath = storage.share(self.vdisk_file_path)
        self.vshare.ui.textareav.setText(self.vdisk_file_path+'\n'+sharepath)
        
        QtCore.QObject.connect(self.vshare.ui.button_submit, QtCore.SIGNAL("clicked()"),
                               self.vdisk_share_submit)
        QtCore.QObject.connect(self.vshare.ui.button_reset, QtCore.SIGNAL("clicked()"),
                               self.vdisk_share_reset)
        QtCore.QObject.connect(self.vshare.ui.button_exit, QtCore.SIGNAL("clicked()"),
                               self.vdisk_share_exit)
            
            
        self.vshare.exec_()
        
    def vdisk_share_submit(self):
        """
        submit the info about the email
        """
        
        if self.vdisk_handler != None:       
            
            receivers = str(self.vshare.ui.tvrec.text())
            receivers = receivers.split(',')
            
            email = CloudBackup.mail.send_mail(receivers,str(self.vshare.ui.tvtopic.text()),
                                               str(self.vshare.ui.textareav.toPlainText()))
            if email:
                mbox = QtGui.QMessageBox()
                mbox.setText("Send Successful!")
                mbox.setWindowTitle("Info")
                mbox.exec_()
            else:
                mbox = QtGui.QMessageBox()
                mbox.setText("Send Failed!")
                mbox.setWindowTitle("Info")
                mbox.exec_()
        else:
            return
    
    def vdisk_share_reset(self):
        """
        clear the info about the email
        """
    
        self.vshare.ui.textareav.clear()
        self.vshare.ui.tvrec.clear()
        self.vshare.ui.tvtopic.clear()
        
    def vdisk_share_exit(self):
        """
        exit the email window
        """
        
        self.vshare.close()       
           
    def vdisk_log_flush(self):
        """
        flush the log display
        """
        
        self.vdisk_show_logs()
        

    """
    the button action associated with the s3 syn file-dir
    """ 
    
    def s3_syn_dir(self):
        """
        select a syn folder
        """ 
        
        filedir = self.file_dir()
        self.ui.tsdirpath.setText(filedir)
    
    def s3_dir_reset(self):
        """
        stop the current syn folder , clear all the associated info
        """
        
        self.ui.tsdirpath.clear()
        self.env.stop_s3()
           
    def s3_dir_submit(self):
        """
        submit the cloud info so that the selected folder become the syn folder
        """ 
        
        if self.suserstate == False:
           
            self.slogin = QtGui.QDialog()
            self.slogin.ui = S3Login_UI.Ui_S3CloudLoginUI()
            self.slogin.ui.setupUi(self.slogin)
            
            QtCore.QObject.connect(self.slogin.ui.button_submit, QtCore.SIGNAL("clicked()"),
                               self.s3_login_submit)
            QtCore.QObject.connect(self.slogin.ui.button_reset, QtCore.SIGNAL("clicked()"),
                               self.s3_login_reset)
            
            
            self.slogin.exec_()
        else:
            self.s3_setup(self.s3_user,self.s3_pwd)
           
    def s3_login_submit(self):
        """
        submit the cloud info to the cloud , show the files and the logs that  synchronized with the cloud
        """
        
        user = self.slogin.ui.ts_access_key.text()
        pwd = self.slogin.ui.ts_secret_access_key.text()
        self.s3_user = user
        self.s3_pwd = pwd
    
        self.s3_setup(user, pwd)
        
        self.ui.lsuserstate.setText("Hello , "+user)   
        self.slogin.close()
    
    def s3_setup(self,user,pwd):   
        """
        use the info of the cloud submitted to setup the cloud storage syn folder 
        """
        
        try:
            
            if self.ui.tsdirpath.text() == "":
                errorbox = QtGui.QMessageBox()
                errorbox.setText("The SynFolder is Empty!")
                errorbox.setWindowTitle("Error")
                errorbox.exec_()
                
            self.s3_handler = self.env.setup_s3(str(user),str(pwd),str(self.ui.tsdirpath.text()),str('cldbkp_'+str(user)).lower())
            self.suserstate = True              
            
            self.ui.StreeWidget.clear()
            value = QtCore.QString(QtGui.QApplication.translate("Directory", "根目录", None, QtGui.QApplication.UnicodeUTF8))
            stringlist = QtCore.QStringList(value)
            root = QtGui.QTreeWidgetItem(stringlist)
            self.ui.StreeWidget.addTopLevelItem(root)
            
            self.s3_show_files(par = root)     
            self.s3_show_logs()
            
        except S3Error, e:
            
            message = e.msg
            errorbox = QtGui.QMessageBox()
            errorbox.setText("Login Failed")
            errorbox.setWindowTitle("Error")
            errorbox.setInformativeText(message)
            errorbox.exec_()
        
    def s3_show_files(self,path = '',par = None):
        """
        show the files that  synchronized with the cloud
        """
        
        if self.s3_handler != None :
            
            for theone in self.s3_handler.list_cloud(path):
                if theone is None: return
                
                if type(theone) is CloudFile :
                    filename = theone.path.split('/')[-1]
                    value = QtCore.QString(filename)
                    stringlist = QtCore.QStringList(value)
                    thefile =  QtGui.QTreeWidgetItem(stringlist)              
                    par.addChild(thefile)
                        
                elif type(theone) is CloudFolder :
                    foldername = theone.path.split('/')[-1]
                    value = QtCore.QString(foldername)
                    stringlist = QtCore.QStringList(value)
                    folder =  QtGui.QTreeWidgetItem(stringlist)
                    par.addChild(folder)
                    self.s3_show_files(foldername,folder)
                
    def s3_show_logs(self):
        """
        show the logs about files that synchronized with the cloud
        """
        
        self.ui.SlogTreeWidget.clear()
        
        for log in self.s3_handler.log_obj.get_logs():
            
            if log is None : return
            
            stime = ' '.join((log.split(' ')[0], log.split(' ')[1]))
            saction = ' '.join((log.split(' ')[2],log.split(' ')[3],log.split(' ')[4]))
            
            log =  QtGui.QTreeWidgetItem()
            log.setText(0,stime)
            log.setText(1,saction)
            
            self.ui.SlogTreeWidget.addTopLevelItem(log)
       
    def s3_login_reset(self):
        """
        clear the info about the account in the cloud
        """
        
        self.slogin.ui.ts_access_key.clear()
        self.slogin.ui.ts_secret_access_key.clear()
        
    def s3_file_share(self):
        """
        share a syn file to others by email
        """
        
        self.s3_file_path = self.get_cloud_path(self.ui.StreeWidget)
        
        if self.s3_file_path is None: return
        
        self.sshare = QtGui.QDialog()
        self.sshare.ui = S3Share_UI.Ui_S3_Share()
        self.sshare.ui.setupUi(self.sshare)
        
        self.sshare.ui.tsrec.setToolTip(QtCore.QString("split the addresses with ',' "))
        
        storage = self.s3_handler.storage
        sharepath = storage.share(self.s3_file_path)
        self.sshare.ui.textareas.setText(self.s3_file_path+'\n'+sharepath)
        
        QtCore.QObject.connect(self.sshare.ui.button_submit, QtCore.SIGNAL("clicked()"),
                               self.s3_share_submit)
        QtCore.QObject.connect(self.sshare.ui.button_reset, QtCore.SIGNAL("clicked()"),
                               self.s3_share_reset)
        QtCore.QObject.connect(self.sshare.ui.button_exit, QtCore.SIGNAL("clicked()"),
                               self.s3_share_exit)
            
            
        self.sshare.exec_()
        
    def s3_share_submit(self):
        """
        submit the info about the email
        """
        
        if self.s3_handler != None:       
            
            receivers = str(self.sshare.ui.tsrec.text())
            receivers = receivers.split(',')
            
            email = CloudBackup.mail.send_mail(receivers,str(self.sshare.ui.tstopic.text()),
                                               str(self.sshare.ui.textareas.toPlainText()))
            if email:
                mbox = QtGui.QMessageBox()
                mbox.setText("Send Successful!")
                mbox.setWindowTitle("Info")
                mbox.exec_()
            else:
                mbox = QtGui.QMessageBox()
                mbox.setText("Send Failed!")
                mbox.setWindowTitle("Info")
                mbox.exec_()
        else:
            return
        
    def s3_share_reset(self):
        """
        clear the info about the email
        """
        
        self.sshare.ui.textareas.clear()
        self.sshare.ui.tsrec.clear()
        self.sshare.ui.tstopic.clear()
        
    def s3_share_exit(self):
        """
        exit the email window
        """
        
        self.sshare.close()       
           
    def s3_log_flush(self):
        """
        flush the log display
        """
        
        self.s3_show_logs()
        
        
    """
    The button action associated with the googlecloud syn file-dir
    """ 
    
    def gs_syn_dir(self):
        """
        select a syn folder
        """
         
        filedir = self.file_dir()
        self.ui.tgdirpath.setText(filedir)
        
    def gs_dir_reset(self):
        """
        stop the current syn folder , clear all the associated info
        """
         
        self.ui.tgdirpath.clear()
        self.env.stop_gs()
        
    def gs_dir_submit(self):
        """
        submit the cloud info so that the selected folder become the syn folder
        """
        
        if self.guserstate == False:
           
            self.glogin = QtGui.QDialog()
            self.glogin.ui = GoogleCloudLogin_UI.Ui_GoogleCloudLoginUI()
            self.glogin.ui.setupUi(self.glogin)
            
            QtCore.QObject.connect(self.glogin.ui.button_submit, QtCore.SIGNAL("clicked()"),
                               self.gs_login_submit)
            QtCore.QObject.connect(self.glogin.ui.button_reset, QtCore.SIGNAL("clicked()"),
                               self.gs_login_reset)
            
            
            self.glogin.exec_()
        else:
            self.gs_setup(self.gs_user,self.gs_pwd,self.gs_pid)
    
    def gs_login_submit(self):
        """
        submit the cloud info to the cloud , show the files and the logs that  synchronized with the cloud
        """
        
        user = self.glogin.ui.tg_access_key.text()
        pwd = self.glogin.ui.tg_secret_access_key.text()
        pid = self.glogin.ui.tg_project_id.text()
        
        self.gs_user = user
        self.gs_pwd = pwd
        self.gs_pid = pid
        
        self.gs_setup(user, pwd, pid)
        
        self.ui.lguserstate.setText("Hello , "+user)       
        self.glogin.close()
    
    def gs_setup(self, user, pwd ,pid):
        """
        use the info of the cloud submitted to setup the cloud storage syn folder 
        """
        
        try:
            
            if self.ui.tgdirpath.text() == "":
                errorbox = QtGui.QMessageBox()
                errorbox.setText("The SynFolder is Empty!")
                errorbox.setWindowTitle("Error")
                errorbox.exec_()
                
            self.gs_handler = self.env.setup_gs(str(user),str(pwd),str(pid),str(self.ui.tgdirpath.text()),str('cldbkp_'+str(user)).lower())
            self.guserstate = True              
            
            self.ui.GtreeWidget.clear()
            value = QtCore.QString(QtGui.QApplication.translate("Directory", "根目录", None, QtGui.QApplication.UnicodeUTF8))
            stringlist = QtCore.QStringList(value)
            root = QtGui.QTreeWidgetItem(stringlist)
            self.ui.GtreeWidget.addTopLevelItem(root)
            
            self.gs_show_files(par = root)          
            self.gs_show_logs()
            
        except  GSError, e:
            
            message = e.msg
            errorbox = QtGui.QMessageBox()
            errorbox.setText("Login Failed")
            errorbox.setWindowTitle("Error")
            errorbox.setInformativeText(message)
            errorbox.exec_()
                  
    def gs_show_files(self,path = '',par = None):
        """
        show the files that  synchronized with the cloud
        """ 
        
        if self.gs_handler != None :
            
            for theone in self.gs_handler.list_cloud(path):
                
                if theone is None: return

                if type(theone) is CloudFile :
                    filename = theone.path.split('/')[-1]
                    value = QtCore.QString(filename)
                    stringlist = QtCore.QStringList(value)
                    thefile =  QtGui.QTreeWidgetItem(stringlist)              
                    par.addChild(thefile)
                        
                elif type(theone) is CloudFolder :
                    foldername = theone.path.split('/')[-1]
                    value = QtCore.QString(foldername)
                    stringlist = QtCore.QStringList(value)
                    folder =  QtGui.QTreeWidgetItem(stringlist)
                    par.addChild(folder)
                    self.gs_show_files(foldername,folder)
                    
    def gs_show_logs(self):
        """
        show the logs about files that synchronized with the cloud
        """
        
        self.ui.GlogTreeWidget.clear()
        if self.gs_handler is None: return
        
        for log in self.gs_handler.log_obj.get_logs():
            if log is None : return

            
            stime = ' '.join((log.split(' ')[0], log.split(' ')[1]))
            saction = ' '.join((log.split(' ')[2],log.split(' ')[3],log.split(' ')[4]))
            
            log =  QtGui.QTreeWidgetItem()
            log.setText(0,stime)
            log.setText(1,saction)
            
            self.ui.GlogTreeWidget.addTopLevelItem(log)
       
    def gs_login_reset(self):
        """
        clear the info about the account in the cloud
        """ 
        
        self.glogin.ui.tg_access_key.clear()
        self.glogin.ui.tg_secret_access_key.clear()
        self.glogin.ui.tg_project_id.clear()
           
    def gs_file_share(self):
        """
        share a syn file to others by email
        """
         
        self.gs_file_path = self.get_cloud_path(self.ui.GtreeWidget)
        
        if self.gs_file_path is None: return
        
        self.gshare = QtGui.QDialog()
        self.gshare.ui = GoogleCloudShare_UI.Ui_GoogleCloud_Share()
        self.gshare.ui.setupUi(self.gshare)
        
        self.gshare.ui.tgrec.setToolTip(QtCore.QString("split the addresses with ',' "))
        
        storage = self.gs_handler.storage
        sharepath = storage.share(self.gs_file_path)
               
        #print self.gs_file_path
        #print sharepath
        
        self.gshare.ui.textareag.setText(self.gs_file_path+'\n'+sharepath)
        
        QtCore.QObject.connect(self.gshare.ui.button_submit, QtCore.SIGNAL("clicked()"),
                               self.gs_share_submit)
        QtCore.QObject.connect(self.gshare.ui.button_reset, QtCore.SIGNAL("clicked()"),
                               self.gs_share_reset)
        QtCore.QObject.connect(self.gshare.ui.button_exit, QtCore.SIGNAL("clicked()"),
                               self.gs_share_exit)
            
            
        self.gshare.exec_()
        
    def gs_share_submit(self):
        """
        submit the info about the email
        """
        
        if self.gs_handler != None:       
            
            receivers = str(self.gshare.ui.tgrec.text())
            receivers = receivers.split(',')
            
            email = CloudBackup.mail.send_mail(receivers,str(self.gshare.ui.tgtopic.text()),
                                               str(self.gshare.ui.textareag.toPlainText()))
            if email:
                mbox = QtGui.QMessageBox()
                mbox.setText("Send Successful!")
                mbox.setWindowTitle("Info")
                mbox.exec_()
            else:
                mbox = QtGui.QMessageBox()
                mbox.setText("Send Failed!")
                mbox.setWindowTitle("Info")
                mbox.exec_()
        else:
            return
    
    def gs_share_reset(self):
        """
        clear the info about the email
        """
        
        self.gshare.ui.textareag.clear()
        self.gshare.ui.tgrec.clear()
        self.gshare.ui.tgtopic.clear()
        
    def gs_share_exit(self):
        """
        exit the email window
        """
        
        self.gshare.close()       
           
    def gs_log_flush(self):
        """
        flush the log display
        """
        
        self.gs_show_logs()
    
        
if __name__ == "__main__":
    
    app = QtGui.QApplication(sys.argv)
    
    try:
        
        myapp = Start()
        myapp.show()
        sys.exit(app.exec_())
        
    except Exception , e:
        message = e.msg
        errorbox = QtGui.QMessageBox()
        errorbox.setText("Operation Failed")
        errorbox.setWindowTitle("Error")
        errorbox.setInformativeText(message)
        errorbox.exec_()

    
        
        
        