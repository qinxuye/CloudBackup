# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GoogleCloudShare.ui'
#
# Created: Fri May 25 19:06:21 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_GoogleCloud_Share(object):
    def setupUi(self, GoogleCloud_Share):
        GoogleCloud_Share.setObjectName(_fromUtf8("GoogleCloud_Share"))
        GoogleCloud_Share.resize(400, 324)
        self.button_submit = QtGui.QPushButton(GoogleCloud_Share)
        self.button_submit.setGeometry(QtCore.QRect(40, 280, 93, 28))
        self.button_submit.setObjectName(_fromUtf8("button_submit"))
        self.button_exit = QtGui.QPushButton(GoogleCloud_Share)
        self.button_exit.setGeometry(QtCore.QRect(270, 280, 93, 28))
        self.button_exit.setObjectName(_fromUtf8("button_exit"))
        self.button_reset = QtGui.QPushButton(GoogleCloud_Share)
        self.button_reset.setGeometry(QtCore.QRect(160, 280, 93, 28))
        self.button_reset.setObjectName(_fromUtf8("button_reset"))
        self.formLayoutWidget = QtGui.QWidget(GoogleCloud_Share)
        self.formLayoutWidget.setGeometry(QtCore.QRect(40, 20, 321, 54))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setMargin(0)
        self.formLayout.setHorizontalSpacing(15)
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.lgrec = QtGui.QLabel(self.formLayoutWidget)
        self.lgrec.setObjectName(_fromUtf8("lgrec"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.lgrec)
        self.tgrec = QtGui.QLineEdit(self.formLayoutWidget)
        self.tgrec.setObjectName(_fromUtf8("tgrec"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.tgrec)
        self.lgtopic = QtGui.QLabel(self.formLayoutWidget)
        self.lgtopic.setObjectName(_fromUtf8("lgtopic"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.lgtopic)
        self.tgtopic = QtGui.QLineEdit(self.formLayoutWidget)
        self.tgtopic.setObjectName(_fromUtf8("tgtopic"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.tgtopic)
        self.verticalLayoutWidget = QtGui.QWidget(GoogleCloud_Share)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(40, 80, 321, 21))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lgcontext = QtGui.QLabel(self.verticalLayoutWidget)
        self.lgcontext.setObjectName(_fromUtf8("lgcontext"))
        self.verticalLayout.addWidget(self.lgcontext)
        self.verticalLayoutWidget_2 = QtGui.QWidget(GoogleCloud_Share)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(40, 110, 321, 151))
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.textareag = QtGui.QTextEdit(self.verticalLayoutWidget_2)
        self.textareag.setObjectName(_fromUtf8("textareag"))
        self.verticalLayout_2.addWidget(self.textareag)

        self.retranslateUi(GoogleCloud_Share)
        QtCore.QMetaObject.connectSlotsByName(GoogleCloud_Share)

    def retranslateUi(self, GoogleCloud_Share):
        GoogleCloud_Share.setWindowTitle(QtGui.QApplication.translate("GoogleCloud_Share", "Google用户分享", None, QtGui.QApplication.UnicodeUTF8))
        self.button_submit.setText(QtGui.QApplication.translate("GoogleCloud_Share", "确定", None, QtGui.QApplication.UnicodeUTF8))
        self.button_exit.setText(QtGui.QApplication.translate("GoogleCloud_Share", "退出", None, QtGui.QApplication.UnicodeUTF8))
        self.button_reset.setText(QtGui.QApplication.translate("GoogleCloud_Share", "重置", None, QtGui.QApplication.UnicodeUTF8))
        self.lgrec.setText(QtGui.QApplication.translate("GoogleCloud_Share", "收件人", None, QtGui.QApplication.UnicodeUTF8))
        self.tgrec.setToolTip(QtGui.QApplication.translate("GoogleCloud_Share", "多个邮件之间用逗号隔开", None, QtGui.QApplication.UnicodeUTF8))
        self.lgtopic.setText(QtGui.QApplication.translate("GoogleCloud_Share", "主题", None, QtGui.QApplication.UnicodeUTF8))
        self.tgtopic.setText(QtGui.QApplication.translate("GoogleCloud_Share", "通过CloudBackup分享文件", None, QtGui.QApplication.UnicodeUTF8))
        self.lgcontext.setText(QtGui.QApplication.translate("GoogleCloud_Share", "内容", None, QtGui.QApplication.UnicodeUTF8))

