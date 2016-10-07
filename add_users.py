#!/usr/bin/env python
# encoding: utf-8

import codecs
import sys
import os
import csv
import re

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "msap.settings")
django.setup()

from staff.models import *
from reversion import revisions as reversion
from django.db import transaction

reload(sys)
sys.setdefaultencoding('utf-8')


with open(sys.argv[1], 'rb') as f:
    for row in f:
        s = re.split('[ \t]', row.strip())
        if SiteUser.has_by_fio(s[0], s[1], s[2]):
            print 'Skipping "%s" -- already exist' % row.strip()
        else:
            if SiteUser.has(s[3]):
                print 'Skipping "%s" -- BAG' % row.strip(), s[3]
                continue
            with transaction.atomic(), reversion.create_revision():
                print u'Addind', row.strip()
                u = SiteUser.create(s[1], s[2], s[0], s[3], 'xxx')
                reversion.set_comment("Auto generated by 'add_users.py' from '%s'" % sys.argv[1])
                


        
