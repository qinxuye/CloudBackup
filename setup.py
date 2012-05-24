#!/usr/bin/env python
#coding=utf-8

from distutils.core import setup
import py2exe
import pyDes

includes = ['CloudBackup', 'CloudBackup.lib',
            'CloudBackup.test.settings', 'CloudBackup.test.local_settings',
            'sip', 'PyQt4']
options = {
    'py2exe': {
        'optimize': 2,
        'includes': includes,
        'dll_excludes': [ "mswsock.dll", "powrprof.dll" ],
        'bundle_files': 1,
        'compressed': True,
    }
}
setup(
    options = options,
    zipfile = None,
    windows = [{'script': 'CloudBackup/cloudbackup.py', 'icon_resources': [(1, 'cloudbackup.ico')]}]
    )