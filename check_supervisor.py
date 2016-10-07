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
        sm = row['Научный руководитель']
        fio = row['Научный руководитель'].split(' ')
        if len(fio) < 3:
            print sm, ' -- BAD'
            continue
        if not SiteUser.has_by_fio(fio[0], fio[1], fio[2]):
            print 'User not found', sm
            continue
        if not Teacher.has_by_fio(fio[0], fio[1], fio[2]):
            u = SiteUser.get_by_fio(fio[0], fio[1], fio[2])
            t = Teacher()
            t.user = u
            t.save()
        s = row['Студент'].split(' ')
        if len(s) < 3:
            s.append(u'')
        if Student.has_by_fio(s[0], s[1], s[2]):
            u = Student.get_by_fio(s[0], s[1], s[2])
            t = Teacher.get_by_fio(fio[0], fio[1], fio[2])
            if not ScientificManagement.has_sc_management(u, t):
                ScientificManagement.unactive_all_sm(u)
                sm = ScientificManagement.create_sc_management(u, t)
                print sm

            

