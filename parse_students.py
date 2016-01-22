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

with open(sys.argv[1], 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in spamreader:
        fio = row[0].split(' ')
        email = row[-2]
        g = row[-1].strip('"').split(',')
        if not SiteUser.has(email):
            u = SiteUser.create(fio[1], fio[2], fio[0], True, False, email, 'xxx')
            print 'Added', u
        print g
        gr = StudentsGroup.get_or_create(g[0], g[1].replace(' ', ''))
        u = SiteUser.get_by_email(email)
        u.students_group = gr
        u.save()
        print 'Update group %s -> %s' % (u, gr)
