# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'S3Login.ui'
#
# Created: Wed May 23 16:40:49 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_S3CloudLoginUI(object):
    def setupUi(self, S3CloudLoginUI):
        S3CloudLoginUI.setObjectName(_fromUtf8("S3CloudLoginUI"))
        S3CloudLoginUI.resize(370, 224)
        self.formLayoutWidget_4 = QtGui.QWidget(S3CloudLoginUI)
        self.formLayoutWidget_4.setGeometry(QtCore.QRect(20, 30, 331, 101))
        self.formLayoutWidget_4.setObjectName(_fromUtf8("formLayoutWidget_4"))
        self.sFormLayout = QtGui.QFormLayout(self.formLayoutWidget_4)
        self.sFormLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.sFormLayout.setMargin(10)
        self.sFormLayout.setMargin(0)
        self.sFormLayout.setHorizontalSpacing(10)
        self.sFormLayout.setVerticalSpacing(30)
        self.sFormLayout.setObjectName(_fromUtf8("sFormLayout"))
        self.ls_access_key = QtGui.QLabel(self.formLayoutWidget_4)
        self.ls_access_key.setObjectName(_fromUtf8("ls_access_key"))
        self.sFormLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.ls_access_key)
        self.ts_access_key = QtGui.QLineEdit(self.formLayoutWidget_4)
        self.ts_access_key.setObjectName(_fromUtf8("ts_access_key"))
        self.sFormLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.ts_access_key)
        self.ls_secret_access_key = QtGui.QLabel(self.formLayoutWidget_4)
        self.ls_secret_access_key.setObjectName(_fromUtf8("ls_secret_access_key"))
        self.sFormLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.ls_secret_access_key)
        self.ts_secret_access_key = QtGui.QLineEdit(self.formLayoutWidget_4)
        self.ts_secret_access_key.setEchoMode(QtGui.QLineEdit.Normal)
        self.ts_secret_access_key.setObjectName(_fromUtf8("ts_secret_access_key"))
        self.sFormLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.ts_secret_access_key)
        self.gridLayoutWidget = QtGui.QWidget(S3CloudLoginUI)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 160, 331, 39))
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

        self.retranslateUi(S3CloudLoginUI)
        QtCore.QMetaObject.connectSlotsByName(S3CloudLoginUI)

    def retranslateUi(self, S3CloudLoginUI):
        S3CloudLoginUI.setWindowTitle(QtGui.QApplication.translate("S3CloudLoginUI", "S3登陆", None, QtGui.QApplication.UnicodeUTF8))
        self.ls_access_key.setText(QtGui.QApplication.translate("S3CloudLoginUI", "ACCESS_KEY", None, QtGui.QApplication.UnicodeUTF8))
        self.ls_secret_access_key.setText(QtGui.QApplication.translate("S3CloudLoginUI", "SECRET_ACCESS_KEY", None, QtGui.QApplication.UnicodeUTF8))
        self.button_submit.setText(QtGui.QApplication.translate("S3CloudLoginUI", "提交", None, QtGui.QApplication.UnicodeUTF8))
        self.button_reset.setText(QtGui.QApplication.translate("S3CloudLoginUI", "重置", None, QtGui.QApplication.UnicodeUTF8))

