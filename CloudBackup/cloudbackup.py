#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-5-23

@author: Chine
'''

import sys
import os

from PyQt4 import QtGui

from CloudBackup.ui.main import Start
from CloudBackup.lib.errors import CloudBackupLibError
from CloudBackup.errors import CloudBackupError
from CloudBackup.log import Log

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    try:
        myapp = Start()
        myapp.show()
        sys.exit(app.exec_())
    except CloudBackupLibError, e:
        message = e.msg
        errorbox = QtGui.QMessageBox()
        errorbox.setText("Operation Failed")
        errorbox.setWindowTitle("Error")
        errorbox.setInformativeText(message)
        errorbox.exec_()