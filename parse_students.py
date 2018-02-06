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
        if len(fio) < 3:
            fio.append(u'')
        u = None
        if Student.has_by_email(email):
            u = Student.get_by_email(email)
        if u is None and not Student.has_by_fio(fio[0], fio[1], fio[2]):
            print 'Adding', fio[1], fio[2], fio[0], email
            u = Student.create(fio[1], fio[2], fio[0], email, 'xxx')
            print 'Added', u
        print g
        gr = StudentsGroup.get_or_create(g[0], g[1].replace(' ', ''))
        if u is None:
            u = Student.get_by_fio(fio[0], fio[1], fio[2])
        u.group = gr
        u.save()
        print 'Update group %s -> %s' % (u, gr)
        
        supervisor = row['Научный руководитель'].strip()
        if supervisor and supervisor != '':
            supervisor = supervisor.strip().split(' ')
            if len(supervisor) == 3:
                if not Teacher.has_by_fio(supervisor[0], supervisor[1], supervisor[2]):
                    print 'Cant find teacher:', supervisor[0]
                else:
                    t = Teacher.get_by_fio(supervisor[0], supervisor[1], supervisor[2])
                    if not ScientificManagement.has_sc_management(u, t):
                        ScientificManagement.unactive_all_sm(u)
                        sm = ScientificManagement.create_sc_management(u, t)
                        print sm
            

