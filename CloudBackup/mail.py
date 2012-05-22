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

Created on 2012-5-22

@author: Chine
'''

import smtplib
from email.mime.text import MIMEText

from CloudBackup.test.settings import EMAIL_HOST, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER

def send_mail(to_list, subject, content):
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = ';'.join(to_list)
    
    try:
        s = smtplib.SMTP()
        s.connect(EMAIL_HOST)
        s.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        s.sendmail(EMAIL_HOST_USER , to_list, msg.as_string())
        s.close()
        
        return True
    except Exception, e:
        print str(e)
        return False