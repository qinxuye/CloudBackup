#!/usr/bin/env python
#coding=utf-8

'''
Created on 2012-5-9

@author: zhao yuan
'''

import sys
import os
from PyQt4 import QtCore ,QtGui

from CloudBackup.environment import Environment
from CloudBackup.lib.errors import VdiskError, S3Error, GSError
from CloudBackup.cloud import CloudFile, CloudFolder
from CloudBackup.utils import get_icon_path
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

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent)       
        self.ui = CloudBackup_UI.Ui_CloudBackupUI()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(get_icon_path()))
        
        self.env = Environment()
        
        vdisk_info = self.env.load_vdisk_info()
        if vdisk_info is None:
            self.vuserstate = False
        else:
            self.vdisk_user = vdisk_info['account']
            self.vdisk_pwd = vdisk_info['password']
            self.vuserstate = True
            self.ui.tvdirpath.setText(
                QtCore.QString(vdisk_info['local_folder'].decode('utf-8')))
            is_weibo = vdisk_info['is_weibo']
            encrypt = vdisk_info['encrypt']
            self.vdisk_setup(self.vdisk_user, self.vdisk_pwd, is_weibo, encrypt)
            self.ui.button_v_submit.setText(QtCore.QString(u'正在同步...'))
            self.vdisk_set_userstate(vdisk_info['account'])
            
        s3_info = self.env.load_s3_info()
        if s3_info is None:
            self.suserstate = False
        else:
            self.s3_user = s3_info['access_key']
            self.s3_pwd = s3_info['secret_access_key']
            self.vuserstate = True
            self.ui.tsdirpath.setText(
                QtCore.QString(s3_info['local_folder'].decode('utf-8')))
            encrypt = s3_info['encrypt']
            self.s3_setup(self.s3_user, self.s3_pwd, encrypt)
            self.ui.button_s_submit.setText(QtCore.QString(u'正在同步...'))
            self.s3_set_userstate()
            
        gs_info = self.env.load_gs_info()
        if gs_info is None:
            self.guserstate = False
        else:
            self.gs_user = gs_info['access_key']
            self.gs_pwd = gs_info['secret_access_key']
            self.gs_pid = gs_info['project_id']
            self.guserstate = True
            self.ui.tgdirpath.setText(
                QtCore.QString(gs_info['local_folder'].decode('utf-8')))
            encrypt = gs_info['encrypt']
            self.gs_setup(self.gs_user, self.gs_pwd, self.gs_pid, encrypt)
            self.ui.button_g_submit.setText(QtCore.QString(u'正在同步...'))
            self.gs_set_userstate()
        
        # register the button function under the VDisk syn file-dir
        QtCore.QObject.connect(self.ui.button_v_dir, QtCore.SIGNAL("clicked()"),
                               self.vdisk_syn_dir)
        
        QtCore.QObject.connect(self.ui.button_v_submit, QtCore.SIGNAL("clicked()"),
                               self.vdisk_dir_submit)
        
        QtCore.QObject.connect(self.ui.button_v_reset, QtCore.SIGNAL("clicked()"),
                               self.vdisk_dir_reset)
        
        QtCore.QObject.connect(self.ui.button_v_cloudflush, QtCore.SIGNAL("clicked()"),
                               self.vdisk_cloud_flush)
        
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
        
        QtCore.QObject.connect(self.ui.button_s_cloudflush, QtCore.SIGNAL("clicked()"),
                               self.s3_cloud_flush)
        
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
        
        QtCore.QObject.connect(self.ui.button_g_cloudflush, QtCore.SIGNAL("clicked()"),
                               self.gs_cloud_flush)
        
        QtCore.QObject.connect(self.ui.button_g_share, QtCore.SIGNAL("clicked()"),
                               self.gs_file_share)
        
        QtCore.QObject.connect(self.ui.button_g_logflush, QtCore.SIGNAL("clicked()"),
                               self.gs_log_flush)
    
    def closeEvent(self, event): 
        self.env.stop_vdisk(clear_info=False)
        self.env.stop_s3(clear_info=False)
        self.env.stop_gs(clear_info=False)
        event.accept()    
        
    def alert(self, msg):
        if isinstance(msg, str):
            msg = msg.decode('utf-8')
        
        errorbox = QtGui.QMessageBox()
        errorbox.setText(QtCore.QString(msg))
        errorbox.setWindowTitle(QtCore.QString(u"需要提醒您："))
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
    
    def get_cloud_path(self, tree):
        '''
        get the cloud path of the selected file
        '''
        
        items = tree.selectedItems()
        try:
            path = items[0].toolTip(0)
            path = str(path)
            name = str(items[0].text(0))
            return path, name
        except IndexError,e:
            self.alert(u'请选择要分享的文件！')
            return
    
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
        
        if len(str(self.ui.tvdirpath.text())) == 0:
            self.alert(u"同步文件夹不能为空！")
            return
        if not os.path.exists(str(self.ui.tvdirpath.text())):
            self.alert(u"你所设置的路径不存在！")
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
            vdisk_info = self.env.load_vdisk_info()
            args = tuple([vdisk_info[k] for k in 
                    ('account', 'password', 'is_weibo', 'encrypt', 'encrypt_code')])
            self.vdisk_setup(*args)
            
    def vdisk_login_submit(self):
        """
        submit the cloud info to the cloud , show the files and the logs that  synchronized with the cloud
        """
        
        user = str(self.vlogin.ui.tvuser.text())
        pwd = str(self.vlogin.ui.tvpwd.text())
        is_weibo = self.vlogin.ui.tvisweibo.isChecked()
        encrypt = self.vlogin.ui.tvencrypt.isChecked()
        
        success = self.vdisk_setup(user, pwd, is_weibo, encrypt)
        if success:
            self.vdisk_user = user
            self.vdisk_pwd = pwd
            self.vdisk_set_userstate(user)
                   
            self.vlogin.close()
        
    def vdisk_set_userstate(self, user):
        self.ui.lvuserstate.setText(
            QtCore.QString(("Hello, 微盘用户 %s" % user).decode('utf-8')))
        
        
    def vdisk_setup(self, user, pwd, is_weibo=False, encrypt=False, encrypt_code=None):     
        """
        use the info of the cloud submitted to setup the cloud storage syn folder 
        """
        
        try:
            if len(str(self.ui.tvdirpath.text())) == 0:
                self.alert(u"同步文件夹不能为空！")
                return
            
            local_folder = str(self.ui.tvdirpath.text())
            
            vdisk_info = self.env.load_vdisk_info()
            force_stop = False
            if vdisk_info is not None:
                for k, v in {'account': user, 
                             'password': pwd, 
                             'local_folder': local_folder,
                             'is_weibo': is_weibo,
                             'encrypt': encrypt,
                             'encrypt_code': encrypt_code }.iteritems():
                    if k not in vdisk_info or vdisk_info[k] != v:
                        force_stop = True
                        break
            
            if encrypt:
                holder = 'cldbkp_%s_encrypt' % str(user)
                if not encrypt_code:
                    if len(self.vdisk_user) >= 8:
                        encrypt_code = self.vdisk_user[:8]
                    else:
                        encrypt_code = self.vdisk_user + '*' * (8 - len(self.vdisk_user))
            else:
                holder = 'cldbkp_%s' % str(user)
            
            self.vdisk_handler = self.env.setup_vdisk(
                str(user), str(pwd), local_folder, holder,
                is_weibo=is_weibo, encrypt=encrypt, encrypt_code=encrypt_code, 
                force_stop=force_stop)
            self.vuserstate = True      
            self.vdisk_user = str(user)
            
            self.ui.VtreeWidget.clear()
            value = QtCore.QString(QtGui.QApplication.translate("Directory", "根目录", None, QtGui.QApplication.UnicodeUTF8))
            stringlist = QtCore.QStringList(value)
            root = QtGui.QTreeWidgetItem(stringlist)
            self.ui.VtreeWidget.addTopLevelItem(root)
            
            self.vdisk_show_files(par=root)       
            self.vdisk_show_logs()
            
            return True
        except VdiskError:
            self.alert('登录失败！')
            return False

    
    def vdisk_show_files(self, path='', par=None):
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
                    thefile.setToolTip(0, QtCore.QString(theone.cloud_path))            
                    par.addChild(thefile)
                        
                elif isinstance(theone, CloudFolder):
                    foldername = theone.path.split('/')[-1]
                    value = QtCore.QString(foldername.decode('utf-8'))
                    stringlist = QtCore.QStringList(value)
                    folder =  QtGui.QTreeWidgetItem(stringlist)
                    par.addChild(folder)
                    self.vdisk_show_files(foldername, folder)              
                    
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
        
        
    def vdisk_cloud_flush(self):
        '''
        Flush the cloud fiels.
        '''
        self.ui.VtreeWidget.clear()
        
        value = QtCore.QString(QtGui.QApplication.translate("Directory", "根目录", None, QtGui.QApplication.UnicodeUTF8))
        stringlist = QtCore.QStringList(value)
        root = QtGui.QTreeWidgetItem(stringlist)
        self.ui.VtreeWidget.addTopLevelItem(root)
        
        self.vdisk_show_files(par=root)       
        
    def vdisk_file_share(self):
        """
        share a syn file to others by email
        """
        
        self.vdisk_file_path, self.vdisk_file_name = self.get_cloud_path(self.ui.VtreeWidget)
        
        if self.vdisk_file_path is None or len(str(self.vdisk_file_path)) == 0: 
            self.alert('不支持文件夹分享，请选择文件')
            return
        
        self.vshare = QtGui.QDialog()
        self.vshare.ui = VDiskShare_UI.Ui_Vdisk_Share()
        self.vshare.ui.setupUi(self.vshare)
        
        storage = self.vdisk_handler.storage
        sharepath = storage.share(self.vdisk_file_path)
        self.vshare.ui.textareav.setText(QtCore.QString(
            u'微盘用户%s通过邮件向你分享文件“%s”，下载地址：%s' % \
            (self.vdisk_user, self.vdisk_file_name, sharepath))
        )
        
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
            receivers = receivers.replace('，', ',').split(',')
            
            email = CloudBackup.mail.send_mail(receivers,str(self.vshare.ui.tvtopic.text()),
                                               str(self.vshare.ui.textareav.toPlainText()))
            if email:
                self.vshare.close()
                self.alert(u'发送成功！')
            else:
                self.alert(u'发送失败！')
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
        
        if len(str(self.ui.tsdirpath.text())) == 0:
            self.alert(u"同步文件夹不能为空！")
            return
        if not os.path.exists(str(self.ui.tsdirpath.text())):
            self.alert(u"你所设置的路径不存在！")
            return
        
        if self.suserstate == False:
           
            self.slogin = QtGui.QDialog()
            self.slogin.ui = S3Login_UI.Ui_S3CloudLoginUI()
            self.slogin.ui.setupUi(self.slogin)
            
            self.ui.button_v_submit.setText(QtCore.QString(u'正在同步...'))
            
            QtCore.QObject.connect(self.slogin.ui.button_submit, QtCore.SIGNAL("clicked()"),
                               self.s3_login_submit)
            QtCore.QObject.connect(self.slogin.ui.button_reset, QtCore.SIGNAL("clicked()"),
                               self.s3_login_reset)
            
            
            self.slogin.exec_()
        else:
            s3_info = self.env.load_s3_info()
            args = tuple([s3_info[k] for k in 
                    ('access_key', 'secret_access_key', 'encrypt', 'encrypt_code')])
            self.s3_setup(*args)
    
    def s3_set_userstate(self):
        self.ui.lsuserstate.setText(
            QtCore.QString(("Hello, 亚马逊S3用户").decode('utf-8')))
           
    def s3_login_submit(self):
        """
        submit the cloud info to the cloud , show the files and the logs that  synchronized with the cloud
        """
        
        user = self.slogin.ui.ts_access_key.text()
        pwd = self.slogin.ui.ts_secret_access_key.text()
        encrypt = self.slogin.ui.lsencrypt.isChecked()
    
        success = self.s3_setup(user, pwd, encrypt)
        if success:
            self.s3_user = user
            self.s3_pwd = pwd
            self.s3_set_userstate()
            
            self.slogin.close()
    
    def s3_setup(self, user, pwd, encrypt=False, encrypt_code=None):   
        """
        use the info of the cloud submitted to setup the cloud storage syn folder 
        """
        
        try:
            
            if len(str(self.ui.tsdirpath.text())) == 0:
                self.alert(u"同步文件夹不能为空！")
                return
            
            local_folder = str(self.ui.tsdirpath.text())
            
            s3_info = self.env.load_s3_info()
            force_stop = False
            if s3_info is not None:
                for k, v in {'access_key': user, 
                             'secret_access_key': pwd, 
                             'local_folder': local_folder,
                             'encrypt': encrypt,
                             'encrypt_code': encrypt_code }.iteritems():
                    if k not in s3_info or s3_info[k] != v:
                        force_stop = True
                        break
            
            if encrypt:
                holder = 'cldbkp_%s_encrypt' % str(user)
                if not encrypt_code:
                    if len(self.s3_user) >= 8:
                        encrypt_code = self.s3_user[:8]
                    else:
                        encrypt_code = self.s3_user + '*' * (8 - len(self.s3_user))
            else:
                holder = 'cldbkp_%s' % str(user)
            holder = holder.lower()
            
            self.s3_handler = self.env.setup_s3(
                str(user), str(pwd), local_folder, holder,
                encrypt=encrypt, encrypt_code=encrypt_code, force_stop=force_stop)
            self.suserstate = True              
            
            self.ui.StreeWidget.clear()
            value = QtCore.QString(QtGui.QApplication.translate("Directory", "根目录", None, QtGui.QApplication.UnicodeUTF8))
            stringlist = QtCore.QStringList(value)
            root = QtGui.QTreeWidgetItem(stringlist)
            self.ui.StreeWidget.addTopLevelItem(root)
            
            self.s3_show_files(par=root)     
            self.s3_show_logs()
            
            return True
            
        except S3Error:
            self.alert('登录失败！')
            return False
        
    def s3_show_files(self, path='', par=None):
        """
        show the files that  synchronized with the cloud
        """
        
        if self.s3_handler != None :
            
            for theone in self.s3_handler.list_cloud(path):
                if theone is None: return
                
                if isinstance(theone, CloudFile):
                    filename = theone.path.split('/')[-1]
                    value = QtCore.QString(filename.decode('utf-8'))
                    stringlist = QtCore.QStringList(value)
                    thefile =  QtGui.QTreeWidgetItem(stringlist)
                    thefile.setToolTip(0, QtCore.QString(theone.cloud_path))        
                    par.addChild(thefile)
                        
                elif isinstance(theone, CloudFolder):
                    foldername = theone.path.split('/')[-1]
                    value = QtCore.QString(foldername.decode('utf-8'))
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
            
            splits = log.split(' ', 2)
            
            if len(splits) == 3:
                stime = ' '.join((splits[i] for i in range(2)))
                saction = splits[2]
                
                log =  QtGui.QTreeWidgetItem()
                log.setText(0, QtCore.QString(stime))
                log.setText(1, QtCore.QString(saction.decode('utf-8')))
            
                self.ui.SlogTreeWidget.addTopLevelItem(log)
       
    def s3_login_reset(self):
        """
        clear the info about the account in the cloud
        """
        
        self.slogin.ui.ts_access_key.clear()
        self.slogin.ui.ts_secret_access_key.clear()
    
    def s3_cloud_flush(self):
        '''
        Flush the cloud fiels.
        '''
        self.ui.StreeWidget.clear()
        
        value = QtCore.QString(QtGui.QApplication.translate("Directory", "根目录", None, QtGui.QApplication.UnicodeUTF8))
        stringlist = QtCore.QStringList(value)
        root = QtGui.QTreeWidgetItem(stringlist)
        self.ui.StreeWidget.addTopLevelItem(root)
        
        self.s3_show_files(par=root)       
    
    def s3_file_share(self):
        """
        share a syn file to others by email
        """
        
        self.s3_file_path, self.s3_file_name = self.get_cloud_path(self.ui.StreeWidget)
        
        if self.s3_file_path is None or len(str(self.s3_file_path)) == 0: 
            self.alert('不支持文件夹分享，请选择文件')
            return
        
        self.sshare = QtGui.QDialog()
        self.sshare.ui = S3Share_UI.Ui_S3_Share()
        self.sshare.ui.setupUi(self.sshare)
        
        storage = self.s3_handler.storage
        sharepath = storage.share(self.s3_file_path)
        self.sshare.ui.textareas.setText(QtCore.QString(
            u'亚马逊S3用户（id: %s）通过邮件向你分享文件“%s”，下载地址：%s' % \
            (self.s3_user, self.s3_file_name, sharepath))
        )
        
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
            receivers = receivers.replace('，', ',').split(',')
            
            email = CloudBackup.mail.send_mail(receivers,str(self.sshare.ui.tstopic.text()),
                                               str(self.sshare.ui.textareas.toPlainText()))
            if email:
                self.sshare.close()
                self.alert("发送成功！")
            else:
                self.alert("发送失败！")
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
        
        if len(str(self.ui.tgdirpath.text())) == 0:
            self.alert(u"同步文件夹不能为空！")
            return
        if not os.path.exists(str(self.ui.tgdirpath.text())):
            self.alert(u"你所设置的路径不存在！")
            return
        
        if self.guserstate == False:
           
            self.glogin = QtGui.QDialog()
            self.glogin.ui = GoogleCloudLogin_UI.Ui_GoogleCloudLoginUI()
            self.glogin.ui.setupUi(self.glogin)
            
            self.ui.button_v_submit.setText(QtCore.QString(u'正在同步...'))
            
            QtCore.QObject.connect(self.glogin.ui.button_submit, QtCore.SIGNAL("clicked()"),
                               self.gs_login_submit)
            QtCore.QObject.connect(self.glogin.ui.button_reset, QtCore.SIGNAL("clicked()"),
                               self.gs_login_reset)
            
            
            self.glogin.exec_()
        else:
            gs_info = self.env.load_gs_info()
            args = tuple([gs_info[k] for k in 
                    ('access_key', 'secret_access_key', 'project_id', 'encrypt', 'encrypt_code')])
            self.gs_setup(*args)
    
    def gs_set_userstate(self):
        self.ui.lguserstate.setText(
            QtCore.QString(("Hello, Google云存储用户").decode('utf-8')))
    
    def gs_login_submit(self):
        """
        submit the cloud info to the cloud , show the files and the logs that  synchronized with the cloud
        """
        
        user = self.glogin.ui.tg_access_key.text()
        pwd = self.glogin.ui.tg_secret_access_key.text()
        pid = self.glogin.ui.tg_project_id.text()
        encrypt = self.glogin.ui.tgencrypt.isChecked()
        
        success = self.gs_setup(user, pwd, pid, encrypt)
        if success:
            self.gs_user = user
            self.gs_pwd = pwd
            self.gs_set_userstate()
            
            self.glogin.close()
    
    def gs_setup(self, user, pwd ,pid, encrypt=False, encrypt_code=None):
        """
        use the info of the cloud submitted to setup the cloud storage syn folder 
        """
        
        try:
            
            if len(str(self.ui.tgdirpath.text())) == 0:
                self.alert(u"同步文件夹不能为空！")
                return
            
            local_folder = str(self.ui.tgdirpath.text())
            
            gs_info = self.env.load_gs_info()
            force_stop = False
            if gs_info is not None:
                for k, v in {'access_key': user, 
                             'secret_access_key': pwd, 
                             'project_id': pid,
                             'local_folder': local_folder,
                             'encrypt': encrypt,
                             'encrypt_code': encrypt_code }.iteritems():
                    if k not in gs_info or gs_info[k] != v:
                        force_stop = True
                        break
            
            if encrypt:
                holder = 'cldbkp_%s_encrypt' % str(user)
                if not encrypt_code:
                    if len(self.gs_user) >= 8:
                        encrypt_code = self.gs_user[:8]
                    else:
                        encrypt_code = self.gs_user + '*' * (8 - len(self.gs_user))
            else:
                holder = 'cldbkp_%s' % str(user)
            holder = holder.lower()
                
            self.gs_handler = self.env.setup_gs(
                str(user), str(pwd), str(pid), local_folder, holder,
                encrypt=encrypt, encrypt_code=encrypt_code, force_stop=force_stop)
            self.guserstate = True              
            
            self.ui.GtreeWidget.clear()
            value = QtCore.QString(QtGui.QApplication.translate("Directory", "根目录", None, QtGui.QApplication.UnicodeUTF8))
            stringlist = QtCore.QStringList(value)
            root = QtGui.QTreeWidgetItem(stringlist)
            self.ui.GtreeWidget.addTopLevelItem(root)
            
            self.gs_show_files(par = root)          
            self.gs_show_logs()
            
            return True
            
        except  GSError, e:
            
            self.alert('登录失败！')
            return False
                  
    def gs_show_files(self, path='', par=None):
        """
        show the files that  synchronized with the cloud
        """ 
        
        if self.gs_handler != None :
            
            for theone in self.gs_handler.list_cloud(path):
                
                if theone is None: return

                if isinstance(theone, CloudFile):
                    filename = theone.path.split('/')[-1]
                    value = QtCore.QString(filename.decode('utf-8'))
                    stringlist = QtCore.QStringList(value)
                    thefile =  QtGui.QTreeWidgetItem(stringlist)         
                    thefile.setToolTip(0, QtCore.QString(theone.cloud_path))      
                    par.addChild(thefile)
                        
                elif isinstance(theone, CloudFolder):
                    foldername = theone.path.split('/')[-1]
                    value = QtCore.QString(foldername.decode('utf-8'))
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

            splits = log.split(' ', 2)
            
            if len(splits) == 3:
                stime = ' '.join((splits[i] for i in range(2)))
                saction = splits[2]
                
                log =  QtGui.QTreeWidgetItem()
                log.setText(0, QtCore.QString(stime))
                log.setText(1, QtCore.QString(saction.decode('utf-8')))
            
                self.ui.GlogTreeWidget.addTopLevelItem(log)
       
    def gs_login_reset(self):
        """
        clear the info about the account in the cloud
        """ 
        
        self.glogin.ui.tg_access_key.clear()
        self.glogin.ui.tg_secret_access_key.clear()
        self.glogin.ui.tg_project_id.clear()
    
    def gs_cloud_flush(self):
        '''
        Flush the cloud fiels.
        '''
        self.ui.GtreeWidget.clear()
        
        value = QtCore.QString(QtGui.QApplication.translate("Directory", "根目录", None, QtGui.QApplication.UnicodeUTF8))
        stringlist = QtCore.QStringList(value)
        root = QtGui.QTreeWidgetItem(stringlist)
        self.ui.GtreeWidget.addTopLevelItem(root)
        
        self.gs_show_files(par=root)       
           
    def gs_file_share(self):
        """
        share a syn file to others by email
        """
        
        self.gs_file_path, self.gs_file_name = self.get_cloud_path(self.ui.GtreeWidget)
        
        if self.gs_file_path is None or len(str(self.gs_file_path)) == 0: 
            self.alert('不支持文件夹分享，请选择文件')
            return
        
        self.gshare = QtGui.QDialog()
        self.gshare.ui = GoogleCloudShare_UI.Ui_GoogleCloud_Share()
        self.gshare.ui.setupUi(self.gshare)
        
        storage = self.gs_handler.storage
        sharepath = storage.share(self.gs_file_path)
        self.gshare.ui.textareag.setText(QtCore.QString(
            u'Google云存储用户（id: %s）通过邮件向你分享文件“%s”，下载地址：%s' % \
            (self.gs_user, self.gs_file_name, sharepath))
        )
        
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
            receivers = receivers.replace('，', ',').split(',')
            
            email = CloudBackup.mail.send_mail(receivers,str(self.gshare.ui.tgtopic.text()),
                                               str(self.gshare.ui.textareag.toPlainText()))
            if email:
                self.gshare.close()
                self.alert("发送成功！")
            else:
                self.alert("发送失败！")
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
