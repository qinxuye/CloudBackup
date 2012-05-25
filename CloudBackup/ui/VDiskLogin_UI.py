# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VDiskLogin.ui'
#
# Created: Fri May 25 16:53:37 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_VDiskCloudLoginUI(object):
    def setupUi(self, VDiskCloudLoginUI):
        VDiskCloudLoginUI.setObjectName(_fromUtf8("VDiskCloudLoginUI"))
        VDiskCloudLoginUI.resize(390, 272)
        self.formLayoutWidget = QtGui.QWidget(VDiskCloudLoginUI)
        self.formLayoutWidget.setGeometry(QtCore.QRect(40, 30, 311, 182))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.vFormLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.vFormLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.vFormLayout.setMargin(10)
        self.vFormLayout.setMargin(0)
        self.vFormLayout.setHorizontalSpacing(10)
        self.vFormLayout.setVerticalSpacing(30)
        self.vFormLayout.setObjectName(_fromUtf8("vFormLayout"))
        self.lvuser = QtGui.QLabel(self.formLayoutWidget)
        self.lvuser.setObjectName(_fromUtf8("lvuser"))
        self.vFormLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.lvuser)
        self.tvuser = QtGui.QLineEdit(self.formLayoutWidget)
        self.tvuser.setObjectName(_fromUtf8("tvuser"))
        self.vFormLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.tvuser)
        self.lvpwd = QtGui.QLabel(self.formLayoutWidget)
        self.lvpwd.setObjectName(_fromUtf8("lvpwd"))
        self.vFormLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.lvpwd)
        self.tvpwd = QtGui.QLineEdit(self.formLayoutWidget)
        self.tvpwd.setEchoMode(QtGui.QLineEdit.Password)
        self.tvpwd.setObjectName(_fromUtf8("tvpwd"))
        self.vFormLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.tvpwd)
        self.tvencrypt = QtGui.QCheckBox(self.formLayoutWidget)
        self.tvencrypt.setObjectName(_fromUtf8("tvencrypt"))
        self.vFormLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.tvencrypt)
        self.tvisweibo = QtGui.QCheckBox(self.formLayoutWidget)
        self.tvisweibo.setObjectName(_fromUtf8("tvisweibo"))
        self.vFormLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.tvisweibo)
        self.gridLayoutWidget = QtGui.QWidget(VDiskCloudLoginUI)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(40, 220, 311, 39))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(10, -1, 10, 0)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.button_submit = QtGui.QPushButton(self.gridLayoutWidget)
        self.button_submit.setObjectName(_fromUtf8("button_submit"))
        self.gridLayout.addWidget(self.button_submit, 0, 0, 1, 1)
        self.button_reset = QtGui.QPushButton(self.gridLayoutWidget)
        self.button_reset.setObjectName(_fromUtf8("button_reset"))
        self.gridLayout.addWidget(self.button_reset, 0, 1, 1, 1)

        self.retranslateUi(VDiskCloudLoginUI)
        QtCore.QMetaObject.connectSlotsByName(VDiskCloudLoginUI)

    def retranslateUi(self, VDiskCloudLoginUI):
        VDiskCloudLoginUI.setWindowTitle(QtGui.QApplication.translate("VDiskCloudLoginUI", "VDisk登陆", None, QtGui.QApplication.UnicodeUTF8))
        self.lvuser.setText(QtGui.QApplication.translate("VDiskCloudLoginUI", "用户名称", None, QtGui.QApplication.UnicodeUTF8))
        self.lvpwd.setText(QtGui.QApplication.translate("VDiskCloudLoginUI", "云端密码", None, QtGui.QApplication.UnicodeUTF8))
        self.tvencrypt.setText(QtGui.QApplication.translate("VDiskCloudLoginUI", "是否加密", None, QtGui.QApplication.UnicodeUTF8))
        self.tvisweibo.setText(QtGui.QApplication.translate("VDiskCloudLoginUI", "新浪微博用户", None, QtGui.QApplication.UnicodeUTF8))
        self.button_submit.setText(QtGui.QApplication.translate("VDiskCloudLoginUI", "提交", None, QtGui.QApplication.UnicodeUTF8))
        self.button_reset.setText(QtGui.QApplication.translate("VDiskCloudLoginUI", "重置", None, QtGui.QApplication.UnicodeUTF8))

