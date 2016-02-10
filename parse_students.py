#!/usr/bin/env python
# encoding: utf-8

import codecs
import sys
import os
import csv

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "msap.settings")
django.setup()

from staff.models import *
from contingent.models import *

with open(sys.argv[1], 'rb') as csvfile:
    spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in spamreader:
        fio = row['Студент'].split(' ')
        email = row['Адрес электронной почты']
        if email == '':
            email = row['Адрес электронной почты физтех']            
        g = row['Группа, Год основания, Наименование'].strip('"').split(',')
        if not Student.has_by_email(email):
            if len(fio) > 2:
                u = Student.create(fio[1], fio[2], fio[0], email, 'xxx')
            else:
                u = Student.create(fio[1], u'', fio[0], email, 'xxx')
            print 'Added', u
        print g
        gr = StudentsGroup.get_or_create(g[0], g[1].replace(' ', ''))
        u = Student.get_by_email(email)
        u.group = gr
        u.save()
        print 'Update group %s -> %s' % (u, gr)
