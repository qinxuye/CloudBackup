#!/usr/bin/env python
#coding=utf-8
'''
Created on 2012-4-24

@author: Chine
'''

# Vdisk
VDISK_APP_KEY = ''
VDISK_APP_SECRET = ''
VDISK_TEST_ACCOUNT = ''
VDISK_TEST_PASSWORD = ''

# Amazon S3
S3_ACCESS_KEY = ''
S3_SECRET_ACCESS_KEY = ''
S3_CANONICAL_USER_ID = ''
S3_USER_DISPLAY_NAME = ''

# Google Cloud Storage
GS_ACCESS_KEY = ''
GS_SECRET_ACCESS_KEY = ''
GS_PROJECT_ID = ''
GS_USER_ID = ''

try:
    from local_settings import *
except ImportError:
    pass