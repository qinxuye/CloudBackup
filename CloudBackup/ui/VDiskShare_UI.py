# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VDiskShare.ui'
#
# Created: Wed May 23 15:06:58 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Vdisk_Share(object):
    def setupUi(self, Vdisk_Share):
        Vdisk_Share.setObjectName(_fromUtf8("Vdisk_Share"))
        Vdisk_Share.resize(400, 328)
        self.formLayoutWidget = QtGui.QWidget(Vdisk_Share)
        self.formLayoutWidget.setGeometry(QtCore.QRect(40, 30, 321, 54))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setMargin(0)
        self.formLayout.setHorizontalSpacing(15)
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.lvrec = QtGui.QLabel(self.formLayoutWidget)
        self.lvrec.setObjectName(_fromUtf8("lvrec"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.lvrec)
        self.tvrec = QtGui.QLineEdit(self.formLayoutWidget)
        self.tvrec.setObjectName(_fromUtf8("tvrec"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.tvrec)
        self.lvtopic = QtGui.QLabel(self.formLayoutWidget)
        self.lvtopic.setObjectName(_fromUtf8("lvtopic"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.lvtopic)
        self.tvtopic = QtGui.QLineEdit(self.formLayoutWidget)
        self.tvtopic.setObjectName(_fromUtf8("tvtopic"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.tvtopic)
        self.verticalLayoutWidget = QtGui.QWidget(Vdisk_Share)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(40, 90, 321, 21))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lvcontext = QtGui.QLabel(self.verticalLayoutWidget)
        self.lvcontext.setObjectName(_fromUtf8("lvcontext"))
        self.verticalLayout.addWidget(self.lvcontext)
        self.verticalLayoutWidget_2 = QtGui.QWidget(Vdisk_Share)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(40, 120, 321, 151))
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.textareav = QtGui.QTextEdit(self.verticalLayoutWidget_2)
        self.textareav.setObjectName(_fromUtf8("textareav"))
        self.verticalLayout_2.addWidget(self.textareav)
        self.button_reset = QtGui.QPushButton(Vdisk_Share)
        self.button_reset.setGeometry(QtCore.QRect(160, 290, 93, 28))
        self.button_reset.setObjectName(_fromUtf8("button_reset"))
        self.button_submit = QtGui.QPushButton(Vdisk_Share)
        self.button_submit.setGeometry(QtCore.QRect(40, 290, 93, 28))
        self.button_submit.setObjectName(_fromUtf8("button_submit"))
        self.button_exit = QtGui.QPushButton(Vdisk_Share)
        self.button_exit.setGeometry(QtCore.QRect(270, 290, 93, 28))
        self.button_exit.setObjectName(_fromUtf8("button_exit"))

        self.retranslateUi(Vdisk_Share)
        QtCore.QMetaObject.connectSlotsByName(Vdisk_Share)

    def retranslateUi(self, Vdisk_Share):
        Vdisk_Share.setWindowTitle(QtGui.QApplication.translate("Vdisk_Share", "VDisk用户分享", None, QtGui.QApplication.UnicodeUTF8))
        self.lvrec.setText(QtGui.QApplication.translate("Vdisk_Share", "收件人", None, QtGui.QApplication.UnicodeUTF8))
        self.lvtopic.setText(QtGui.QApplication.translate("Vdisk_Share", "主题", None, QtGui.QApplication.UnicodeUTF8))
        self.lvcontext.setText(QtGui.QApplication.translate("Vdisk_Share", "内容", None, QtGui.QApplication.UnicodeUTF8))
        self.button_reset.setText(QtGui.QApplication.translate("Vdisk_Share", "重置", None, QtGui.QApplication.UnicodeUTF8))
        self.button_submit.setText(QtGui.QApplication.translate("Vdisk_Share", "确定", None, QtGui.QApplication.UnicodeUTF8))
        self.button_exit.setText(QtGui.QApplication.translate("Vdisk_Share", "退出", None, QtGui.QApplication.UnicodeUTF8))

