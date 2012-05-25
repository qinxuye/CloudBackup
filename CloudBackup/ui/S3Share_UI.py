# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'S3Share.ui'
#
# Created: Fri May 25 19:05:23 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_S3_Share(object):
    def setupUi(self, S3_Share):
        S3_Share.setObjectName(_fromUtf8("S3_Share"))
        S3_Share.resize(400, 327)
        self.button_submit = QtGui.QPushButton(S3_Share)
        self.button_submit.setGeometry(QtCore.QRect(40, 280, 93, 28))
        self.button_submit.setObjectName(_fromUtf8("button_submit"))
        self.button_exit = QtGui.QPushButton(S3_Share)
        self.button_exit.setGeometry(QtCore.QRect(270, 280, 93, 28))
        self.button_exit.setObjectName(_fromUtf8("button_exit"))
        self.button_reset = QtGui.QPushButton(S3_Share)
        self.button_reset.setGeometry(QtCore.QRect(160, 280, 93, 28))
        self.button_reset.setObjectName(_fromUtf8("button_reset"))
        self.formLayoutWidget = QtGui.QWidget(S3_Share)
        self.formLayoutWidget.setGeometry(QtCore.QRect(40, 20, 321, 54))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setMargin(0)
        self.formLayout.setHorizontalSpacing(15)
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.lsrec = QtGui.QLabel(self.formLayoutWidget)
        self.lsrec.setObjectName(_fromUtf8("lsrec"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.lsrec)
        self.tsrec = QtGui.QLineEdit(self.formLayoutWidget)
        self.tsrec.setObjectName(_fromUtf8("tsrec"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.tsrec)
        self.lstopic = QtGui.QLabel(self.formLayoutWidget)
        self.lstopic.setObjectName(_fromUtf8("lstopic"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.lstopic)
        self.tstopic = QtGui.QLineEdit(self.formLayoutWidget)
        self.tstopic.setObjectName(_fromUtf8("tstopic"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.tstopic)
        self.verticalLayoutWidget = QtGui.QWidget(S3_Share)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(40, 80, 321, 21))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lscontext = QtGui.QLabel(self.verticalLayoutWidget)
        self.lscontext.setObjectName(_fromUtf8("lscontext"))
        self.verticalLayout.addWidget(self.lscontext)
        self.verticalLayoutWidget_2 = QtGui.QWidget(S3_Share)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(40, 110, 321, 151))
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.textareas = QtGui.QTextEdit(self.verticalLayoutWidget_2)
        self.textareas.setObjectName(_fromUtf8("textareas"))
        self.verticalLayout_2.addWidget(self.textareas)

        self.retranslateUi(S3_Share)
        QtCore.QMetaObject.connectSlotsByName(S3_Share)

    def retranslateUi(self, S3_Share):
        S3_Share.setWindowTitle(QtGui.QApplication.translate("S3_Share", "S3用户分享", None, QtGui.QApplication.UnicodeUTF8))
        self.button_submit.setText(QtGui.QApplication.translate("S3_Share", "确定", None, QtGui.QApplication.UnicodeUTF8))
        self.button_exit.setText(QtGui.QApplication.translate("S3_Share", "退出", None, QtGui.QApplication.UnicodeUTF8))
        self.button_reset.setText(QtGui.QApplication.translate("S3_Share", "重置", None, QtGui.QApplication.UnicodeUTF8))
        self.lsrec.setText(QtGui.QApplication.translate("S3_Share", "收件人", None, QtGui.QApplication.UnicodeUTF8))
        self.tsrec.setToolTip(QtGui.QApplication.translate("S3_Share", "多个邮件之间用逗号隔开", None, QtGui.QApplication.UnicodeUTF8))
        self.lstopic.setText(QtGui.QApplication.translate("S3_Share", "主题", None, QtGui.QApplication.UnicodeUTF8))
        self.tstopic.setText(QtGui.QApplication.translate("S3_Share", "通过CloudBackup分享文件", None, QtGui.QApplication.UnicodeUTF8))
        self.lscontext.setText(QtGui.QApplication.translate("S3_Share", "内容", None, QtGui.QApplication.UnicodeUTF8))

