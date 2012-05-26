#!/usr/bin/env python
#coding=utf-8

'''
Created on 2012-5-9

@author: zhao yuan
'''

import os
import threading
import time
from PyQt4 import QtCore ,QtGui

from CloudBackup.environment import Environment
from CloudBackup.lib.errors import VdiskError, S3Error, GSError
from CloudBackup.cloud import CloudFile, CloudFolder
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
    
class CloudBrowserFlushThread(threading.Thread):
    def __init__(self, base_ui, browser_ui, handler):
        super(CloudBrowserFlushThread, self).__init__()
        self.base_ui = base_ui
        self.ui = browser_ui
        self.handler = handler
        
        self.stopped = False
        self.ensure_quit = False
    
    def generate_cloud_tree(self, path='', parent=None):
        """
        show the files that  synchronized with the cloud
        """
        
        if self.handler is None or self.stopped:
            return
        
        try:
            for itm in self.handler.list_cloud(path):
                if itm is None or self.stopped: return
                
                name = QtCore.QString(itm.path.split('/')[-1].decode('utf-8'))
                widget_itm = QtGui.QTreeWidgetItem(QtCore.QStringList(name))
                
                if isinstance(itm, CloudFile):
                    widget_itm.setToolTip(0, QtCore.QString(itm.cloud_path))            
                    parent.addChild(widget_itm)
                elif isinstance(itm, CloudFolder):
                    parent.addChild(widget_itm)
                    self.generate_cloud_tree(itm.cloud_path, widget_itm)
        except VdiskError, e:
            if e.err_no == 900:
                time.sleep(10)
            else:
                raise e
    
    def cloud_browser_flush(self):
        self.ui.clear()
        root = self.base_ui.add_root_to_cloud_browser(self.ui)
        self.generate_cloud_tree(parent=root)
        self.ensure_quit = True
    
    def run(self):
        self.cloud_browser_flush()
        
    def stop(self):
        self.stopped = True
        
class LogFlushThread(threading.Thread):
    def __init__(self, ui, handler):
        super(LogFlushThread, self).__init__()
        self.ui = ui
        self.handler = handler
        
        self.stopped = False
        
    def show_logs(self):
        if self.handler is None or self.stopped:
            return
        
        self.ui.clear()
        
        for log in self.handler.log_obj.get_logs():
            if log is None or self.stopped: return
            
            splits = log.split(' ', 2)
            
            if len(splits) == 3:
                stime = ' '.join((splits[i] for i in range(2)))
                saction = splits[2]
                
                log =  QtGui.QTreeWidgetItem()
                log.setText(0, QtCore.QString(stime))
                log.setText(1, QtCore.QString(saction.decode('utf-8')))
            
                self.ui.addTopLevelItem(log)
                
    def run(self):
        self.show_logs()
        
    def stop(self):
        self.stopped = True
    
class UI(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent)       
        self.ui = CloudBackup_UI.Ui_CloudBackupUI()
        self.ui.setupUi(self)
        
        self.env = Environment()
        
        self.vdisk_handler = None
        self.s3_handler = None
        self.gs_handler = None
        
        self.vdisk_info = self.env.load_vdisk_info()
        self.s3_info = self.env.load_s3_info()
        self.gs_info = self.env.load_gs_info()
        
        self.vdisk_cloud_browser_thread = None
        self.vdisk_log_thread = None
        self.s3_cloud_browser_thread = None
        self.s3_log_thread = None
        self.gs_cloud_browser_thread = None
        self.gs_log_thread = None
        
        self.vdisk_init()
        self.s3_init()
        self.gs_init()
        
        # register the button function under the VDisk syn file-dir
        QtCore.QObject.connect(self.ui.button_v_dir, QtCore.SIGNAL("clicked()"),
                               self.set_sync_path(self.ui.tvdirpath))
        
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
                               self.set_sync_path(self.ui.tsdirpath))
        
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
                               self.set_sync_path(self.ui.tgdirpath))
        
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
        
    def get_holder(self, key, encrypt=False):
        if encrypt:
            holder = 'cldbkp_%s_encrypt' % str(key)
        else:
            holder = 'cldbkp_%s' % str(key)
        return holder.lower()
    
    def get_encrypt_code(self, key):
        if len(key) >= 8:
            return key[:8]
        return key + '*' * (8 - len(key))
        
    def alert(self, msg):
        if isinstance(msg, str):
            msg = msg.decode('utf-8')
        
        errorbox = QtGui.QMessageBox()
        errorbox.setText(QtCore.QString(msg))
        errorbox.setWindowTitle(QtCore.QString(u"需要提醒您："))
        errorbox.exec_()
        
    def status_set(self, button, status_label, welcome_info):
        button.setText(QtCore.QString(u'正在同步...'))
        if isinstance(welcome_info, str):
            welcome_info = welcome_info.decode('utf-8')
        status_label.setText(QtCore.QString(welcome_info))
        
    def status_reset(self, button, status_label):
        button.setText(QtCore.QString(u'开始同步'))
        status_label.setText(QtCore.QString(u'用户登录状态'))
            
    def choose_dir(self):
        """
        provide a dialog for the user to get the folder
        """  
        
        fd = QtGui.QFileDialog(self)
        filedir = fd.getExistingDirectory(parent=None, caption="File Dir")
                
        return filedir
    
    def set_sync_path(self, ui):
        def _action():
            dir_ = self.choose_dir()
            ui.setText(dir_)
        return _action
    
    def add_root_to_cloud_browser(self, ui):
        value = QtCore.QString(u'根目录')
        stringlist = QtCore.QStringList(value)
        root = QtGui.QTreeWidgetItem(stringlist)
        ui.addTopLevelItem(root)
        
        return root
    
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
        
    def vdisk_init(self):
        if self.vdisk_info is None:
            return
        
        success = self.vdisk_setup(**self.vdisk_info)
        if success:
            self.ui.tvdirpath.setText(
                QtCore.QString(self.vdisk_info['local_folder'].decode('utf-8')))
            self.status_set(self.ui.button_v_submit, 
                            self.ui.lvuserstate, 
                            "Hello, 微盘用户 %s" % self.vdisk_info['account'])
        else:
            self.env.remove_vdisk_info()
            self.vdisk_info = None
        
    def vdisk_dir_reset(self):
        """
        stop the current syn folder , clear all the associated info
        """
        
        self.ui.tvdirpath.clear()
        
        if self.vdisk_cloud_browser_thread:
            self.vdisk_cloud_browser_thread.stop()
        if self.vdisk_log_thread:
            self.vdisk_log_thread.stop()
        self.ui.VtreeWidget.clear()
        self.ui.VlogTreeWidget.clear()
         
        self.env.stop_vdisk()
        self.vdisk_info = None
        self.status_reset(self.ui.button_v_submit, 
                          self.ui.lvuserstate)
        
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
        
        if not self.vdisk_info:
            self.vlogin = QtGui.QDialog()
            self.vlogin.ui = VDiskLogin_UI.Ui_VDiskCloudLoginUI()
            self.vlogin.ui.setupUi(self.vlogin)
            
            QtCore.QObject.connect(self.vlogin.ui.button_submit, QtCore.SIGNAL("clicked()"),
                               self.vdisk_login_submit)
            QtCore.QObject.connect(self.vlogin.ui.button_reset, QtCore.SIGNAL("clicked()"),
                               self.vdisk_login_reset)
            
            self.vlogin.exec_()
        else:
            info = dict(self.vdisk_info)
            info['local_folder'] = str(self.ui.tvdirpath.text())
            success = self.vdisk_setup(**info)
            if not success:
                self.alert('登录失败！')
            
    def vdisk_login_submit(self):
        """
        submit the cloud info to the cloud , show the files and the logs that  synchronized with the cloud
        """
        
        user = str(self.vlogin.ui.tvuser.text())
        pwd = str(self.vlogin.ui.tvpwd.text())
        is_weibo = self.vlogin.ui.tvisweibo.isChecked()
        encrypt = self.vlogin.ui.tvencrypt.isChecked()
        local_folder = str(self.ui.tvdirpath.text())
        
        success = self.vdisk_setup(user, pwd, local_folder, is_weibo, encrypt)
        if success:
            self.status_set(self.ui.button_v_submit, 
                            self.ui.lvuserstate, 
                            "Hello, 微盘用户 %s" % self.vdisk_info['account'])
            self.vlogin.close()
        else:
            self.alert('登录失败！')
        
    def vdisk_setup(self, account, password, local_folder,
                    is_weibo=False, encrypt=False, encrypt_code=None, **kwargs):     
        """
        use the info of the cloud submitted to setup the cloud storage syn folder 
        """
        
        try:
            args = locals()
            del args['self']
            
            force_stop = False
            if self.vdisk_info is not None:
                for k, v in args.iteritems():
                    if k in self.vdisk_info and self.vdisk_info[k] != v:
                        force_stop = True
                        break
            
            holder = self.get_holder(account)
            encrypt_code = self.get_encrypt_code(account) if encrypt else None
            
            self.vdisk_handler = self.env.setup_vdisk(
                account, password, local_folder, holder,
                is_weibo=is_weibo, encrypt=encrypt, encrypt_code=encrypt_code, 
                force_stop=force_stop)
            
            if force_stop or self.vdisk_info is None:
                self.vdisk_info = args
            
            self.vdisk_cloud_flush()
            self.vdisk_show_logs()
            
            return True
        except VdiskError:
            return False              
                    
    def vdisk_show_logs(self):
        """
        show the logs about files that synchronized with the cloud
        """
        
        if self.vdisk_log_thread:
            self.vdisk_log_thread.stop()
            
        self.vdisk_log_thread = LogFlushThread(self.ui.VlogTreeWidget, self.vdisk_handler)
        self.vdisk_log_thread.setDaemon(True)
        self.vdisk_log_thread.start()
    
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
        if self.vdisk_cloud_browser_thread:
            self.vdisk_cloud_browser_thread.stop()
        
        self.vdisk_cloud_browser_thread = CloudBrowserFlushThread(
            self, self.ui.VtreeWidget, self.vdisk_handler)
        self.vdisk_cloud_browser_thread.setDaemon(True)
        self.vdisk_cloud_browser_thread.start()
        
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
        
    def s3_init(self):
        if self.s3_info is None:
            return
        
        success = self.s3_setup(**self.s3_info)
        if success:
            self.ui.tsdirpath.setText(
                QtCore.QString(self.s3_info['local_folder'].decode('utf-8')))
            self.status_set(self.ui.button_s_submit, 
                            self.ui.lsuserstate, 
                            "Hello, 亚马逊S3用户 %s" % self.s3_display_name)
        else:
            self.env.remove_s3_info()
            self.s3_info = None
    
    def s3_dir_reset(self):
        """
        stop the current syn folder , clear all the associated info
        """
        
        self.ui.tsdirpath.clear()
        
        if self.s3_cloud_browser_thread:
            self.s3_cloud_browser_thread.stop()
        if self.s3_log_thread:
            self.s3_log_thread.stop()
        self.ui.StreeWidget.clear()
        self.ui.SlogTreeWidget.clear()
         
        self.env.stop_s3()
        self.s3_info = None
        self.status_reset(self.ui.button_s_submit, 
                          self.ui.lsuserstate)
           
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
        
        if not self.s3_info:
            self.slogin = QtGui.QDialog()
            self.slogin.ui = S3Login_UI.Ui_S3CloudLoginUI()
            self.slogin.ui.setupUi(self.slogin)
            
            QtCore.QObject.connect(self.slogin.ui.button_submit, QtCore.SIGNAL("clicked()"),
                               self.s3_login_submit)
            QtCore.QObject.connect(self.slogin.ui.button_reset, QtCore.SIGNAL("clicked()"),
                               self.s3_login_reset)
            
            self.slogin.exec_()
        else:
            info = dict(self.s3_info)
            info['local_folder'] = str(self.ui.tsdirpath.text())
            success = self.s3_setup(**info)
            if not success:
                self.alert('登录失败！')
           
    def s3_login_submit(self):
        """
        submit the cloud info to the cloud , show the files and the logs that  synchronized with the cloud
        """
        
        access_key = str(self.slogin.ui.ts_access_key.text())
        secret_access_key = str(self.slogin.ui.ts_secret_access_key.text())
        local_folder = str(self.ui.tsdirpath.text())
        encrypt = self.slogin.ui.lsencrypt.isChecked()
        
        success = self.s3_setup(access_key, secret_access_key, local_folder, encrypt)
        if success:
            self.status_set(self.ui.button_s_submit, 
                            self.ui.lsuserstate, 
                            "Hello, 亚马逊S3用户 %s" % self.s3_display_name)
            self.slogin.close()
        else:
            self.alert('登录失败！')
    
    def s3_setup(self, access_key, secret_access_key, local_folder, 
                 encrypt=False, encrypt_code=None, **kwargs):   
        """
        use the info of the cloud submitted to setup the cloud storage syn folder 
        """
        
        try:
            args = locals()
            del args['self']
            
            force_stop = False
            if self.s3_info is not None:
                for k, v in args.iteritems():
                    if k in self.s3_info and self.s3_info[k] != v:
                        force_stop = True
                        break
            
            holder = self.get_holder(access_key)
            encrypt_code = self.get_encrypt_code(access_key) if encrypt else None
            
            self.s3_handler = self.env.setup_s3(
                access_key, secret_access_key, local_folder, holder,
                encrypt=encrypt, encrypt_code=encrypt_code, force_stop=force_stop)          
            
            if force_stop or self.s3_info is None:
                self.s3_info = args
            
            self.s3_cloud_flush()     
            self.s3_show_logs()
            
            self.s3_display_name = self.s3_handler.storage.client.list_buckets()[0].display_name
            
            return True
            
        except S3Error:
            return False
                
    def s3_show_logs(self):
        """
        show the logs about files that synchronized with the cloud
        """
        
        if self.s3_log_thread:
            self.s3_log_thread.stop()
            
        self.s3_log_thread = LogFlushThread(self.ui.SlogTreeWidget, self.s3_handler)
        self.s3_log_thread.setDaemon(True)
        self.s3_log_thread.start()
       
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
        
        if self.s3_cloud_browser_thread:
            self.s3_cloud_browser_thread.stop()
        
        self.s3_cloud_browser_thread = CloudBrowserFlushThread(
            self, self.ui.StreeWidget, self.s3_handler)
        self.s3_cloud_browser_thread.setDaemon(True)
        self.s3_cloud_browser_thread.start()
    
    def s3_file_share(self):
        """
        share a syn file to others by email
        """
        
        s3_file_path, s3_file_name = self.get_cloud_path(self.ui.StreeWidget)
        
        if s3_file_path is None or len(str(s3_file_path)) == 0: 
            self.alert('不支持文件夹分享，请选择文件')
            return
        
        self.sshare = QtGui.QDialog()
        self.sshare.ui = S3Share_UI.Ui_S3_Share()
        self.sshare.ui.setupUi(self.sshare)
        
        storage = self.s3_handler.storage
        sharepath = storage.share(s3_file_path)
        self.sshare.ui.textareas.setText(QtCore.QString(
            u'亚马逊S3用户%s通过邮件向你分享文件“%s”，下载地址：%s' % \
            (self.s3_display_name, s3_file_name, sharepath))
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
        
    def gs_init(self):
        if self.gs_info is None:
            return
        
        success = self.gs_setup(**self.gs_info)
        if success:
            self.ui.tgdirpath.setText(
                QtCore.QString(self.gs_info['local_folder'].decode('utf-8')))
            self.status_set(self.ui.button_g_submit, 
                            self.ui.lguserstate, 
                            "Hello, Google云存储用户")
        else:
            self.env.remove_gs_info()
            self.gs_info = None
        
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
        
        if not self.gs_info:
            self.glogin = QtGui.QDialog()
            self.glogin.ui = GoogleCloudLogin_UI.Ui_GoogleCloudLoginUI()
            self.glogin.ui.setupUi(self.glogin)
            
            QtCore.QObject.connect(self.glogin.ui.button_submit, QtCore.SIGNAL("clicked()"),
                               self.gs_login_submit)
            QtCore.QObject.connect(self.glogin.ui.button_reset, QtCore.SIGNAL("clicked()"),
                               self.gs_login_reset)
            
            self.glogin.exec_()
        else:
            info = dict(self.gs_info)
            info['local_folder'] = str(self.ui.tgdirpath.text())
            success = self.gs_setup(**info)
            if not success:
                self.alert('登录失败！')
    
    def gs_login_submit(self):
        """
        submit the cloud info to the cloud , show the files and the logs that  synchronized with the cloud
        """
        
        access_key = str(self.glogin.ui.tg_access_key.text())
        secret_access_key  = str(self.glogin.ui.tg_secret_access_key.text())
        project_id = str(self.glogin.ui.tg_project_id.text())
        local_folder = str(self.ui.tgdirpath.text())
        encrypt = self.glogin.ui.tgencrypt.isChecked()
        
        success = self.gs_setup(access_key, secret_access_key, project_id, local_folder, encrypt)
        if success:
            self.status_set(self.ui.button_g_submit, 
                            self.ui.lguserstate, 
                            "Hello, Google云存储用户")
            self.glogin.close()
        else:
            self.alert('登录失败！')
    
    def gs_setup(self, access_key, secret_access_key, project_id, local_folder,
                 encrypt=False, encrypt_code=None, **kwargs):
        """
        use the info of the cloud submitted to setup the cloud storage syn folder 
        """
        
        try:
            args = locals()
            del args['self']
            
            force_stop = False
            if self.gs_info is not None:
                for k, v in args.iteritems():
                    if k in self.gs_info and self.gs_info[k] != v:
                        force_stop = True
                        break
            
            holder = self.get_holder(access_key)
            encrypt_code = self.get_encrypt_code(access_key) if encrypt else None
            
            self.gs_handler = self.env.setup_gs(
                access_key, secret_access_key, project_id, local_folder, holder,
                encrypt=encrypt, encrypt_code=encrypt_code, force_stop=force_stop)          
            
            if force_stop or self.gs_info is None:
                self.gs_info = args
            
            self.gs_cloud_flush()    
            self.gs_show_logs()
            
            return True
        except  GSError, e:
            
            self.alert('登录失败！')
            return False
                    
    def gs_show_logs(self):
        """
        show the logs about files that synchronized with the cloud
        """
        
        if self.gs_log_thread:
            self.gs_log_thread.stop()
            
        self.gs_log_thread = LogFlushThread(self.ui.GlogTreeWidget, self.gs_handler)
        self.gs_log_thread.setDaemon(True)
        self.gs_log_thread.start()
       
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
        
        if self.gs_cloud_browser_thread:
            self.gs_cloud_browser_thread.stop()
        
        self.gs_cloud_browser_thread = CloudBrowserFlushThread(
            self, self.ui.GtreeWidget, self.gs_handler)
        self.gs_cloud_browser_thread.setDaemon(True)
        self.gs_cloud_browser_thread.start()    
           
    def gs_file_share(self):
        """
        share a syn file to others by email
        """
        
        gs_file_path, gs_file_name = self.get_cloud_path(self.ui.GtreeWidget)
        
        if gs_file_path is None or len(str(gs_file_path)) == 0: 
            self.alert('不支持文件夹分享，请选择文件')
            return
        
        self.gshare = QtGui.QDialog()
        self.gshare.ui = GoogleCloudShare_UI.Ui_GoogleCloud_Share()
        self.gshare.ui.setupUi(self.gshare)
        
        storage = self.gs_handler.storage
        sharepath = storage.share(gs_file_path)
        self.gshare.ui.textareag.setText(QtCore.QString(
            u'Google云存储用户（id: %s）通过邮件向你分享文件“%s”，下载地址：%s' % \
            (self.gs_info['access_key'], gs_file_name, sharepath))
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
