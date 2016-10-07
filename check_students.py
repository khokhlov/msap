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
        if len(fio) < 3:
            fio.append(u'')
        if not Student.has_by_fio(fio[0], fio[1], fio[2]):
            print fio[1], fio[2], fio[0], ' -- BAD'
            

