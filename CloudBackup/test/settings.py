#!/usr/bin/env python
#coding=utf-8
'''
Copyright (c) 2012 chine <qin@qinxuye.me>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Created on 2012-4-24

@author: Chine
'''

# If you want to compile the cloud backup on windows, please set EXE_COMPILE to True.
EXE_COMPILE = False

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

# Email
EMAIL_HOST = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_HOST_USER = ""
email_port = 25
email_use_tls = True

try:
    from local_settings import *
except ImportError:
    pass