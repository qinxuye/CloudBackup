# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GoogleCloudLogin.ui'
#
# Created: Fri May 25 19:09:51 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_GoogleCloudLoginUI(object):
    def setupUi(self, GoogleCloudLoginUI):
        GoogleCloudLoginUI.setObjectName(_fromUtf8("GoogleCloudLoginUI"))
        GoogleCloudLoginUI.resize(380, 238)
        self.formLayoutWidget_2 = QtGui.QWidget(GoogleCloudLoginUI)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(20, 30, 331, 131))
        self.formLayoutWidget_2.setObjectName(_fromUtf8("formLayoutWidget_2"))
        self.gFormLayout = QtGui.QFormLayout(self.formLayoutWidget_2)
        self.gFormLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.gFormLayout.setMargin(10)
        self.gFormLayout.setMargin(0)
        self.gFormLayout.setSpacing(10)
        self.gFormLayout.setObjectName(_fromUtf8("gFormLayout"))
        self.lg_access_key = QtGui.QLabel(self.formLayoutWidget_2)
        self.lg_access_key.setObjectName(_fromUtf8("lg_access_key"))
        self.gFormLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.lg_access_key)
        self.tg_access_key = QtGui.QLineEdit(self.formLayoutWidget_2)
        self.tg_access_key.setObjectName(_fromUtf8("tg_access_key"))
        self.gFormLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.tg_access_key)
        self.lg_secret_access_key = QtGui.QLabel(self.formLayoutWidget_2)
        self.lg_secret_access_key.setObjectName(_fromUtf8("lg_secret_access_key"))
        self.gFormLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.lg_secret_access_key)
        self.tg_secret_access_key = QtGui.QLineEdit(self.formLayoutWidget_2)
        self.tg_secret_access_key.setObjectName(_fromUtf8("tg_secret_access_key"))
        self.gFormLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.tg_secret_access_key)
        self.lg_project_id = QtGui.QLabel(self.formLayoutWidget_2)
        self.lg_project_id.setObjectName(_fromUtf8("lg_project_id"))
        self.gFormLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.lg_project_id)
        self.tg_project_id = QtGui.QLineEdit(self.formLayoutWidget_2)
        self.tg_project_id.setObjectName(_fromUtf8("tg_project_id"))
        self.gFormLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.tg_project_id)
        self.tgencrypt = QtGui.QCheckBox(self.formLayoutWidget_2)
        self.tgencrypt.setObjectName(_fromUtf8("tgencrypt"))
        self.gFormLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.tgencrypt)
        self.gridLayoutWidget = QtGui.QWidget(GoogleCloudLoginUI)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 170, 331, 39))
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

        self.retranslateUi(GoogleCloudLoginUI)
        QtCore.QMetaObject.connectSlotsByName(GoogleCloudLoginUI)

    def retranslateUi(self, GoogleCloudLoginUI):
        GoogleCloudLoginUI.setWindowTitle(QtGui.QApplication.translate("GoogleCloudLoginUI", "GoogleCloud登陆", None, QtGui.QApplication.UnicodeUTF8))
        self.lg_access_key.setText(QtGui.QApplication.translate("GoogleCloudLoginUI", "ACCESS_KEY", None, QtGui.QApplication.UnicodeUTF8))
        self.lg_secret_access_key.setText(QtGui.QApplication.translate("GoogleCloudLoginUI", "SECRET_ACCESS_KEY", None, QtGui.QApplication.UnicodeUTF8))
        self.lg_project_id.setText(QtGui.QApplication.translate("GoogleCloudLoginUI", "PROJECT_ID", None, QtGui.QApplication.UnicodeUTF8))
        self.tgencrypt.setText(QtGui.QApplication.translate("GoogleCloudLoginUI", "是否加密", None, QtGui.QApplication.UnicodeUTF8))
        self.button_submit.setText(QtGui.QApplication.translate("GoogleCloudLoginUI", "提交", None, QtGui.QApplication.UnicodeUTF8))
        self.button_reset.setText(QtGui.QApplication.translate("GoogleCloudLoginUI", "重置", None, QtGui.QApplication.UnicodeUTF8))

