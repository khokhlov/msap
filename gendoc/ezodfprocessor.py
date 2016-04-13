# coding:utf-8

from __future__ import unicode_literals, print_function
from ezodf import opendoc
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class EzodfTemplateProcessor:
    def __init__(self):
        self.doc = None
    
    def load_template(self, data):
        self.doc = opendoc(data)
    
    def get_vars(self):
        v = self.doc.body.variables
        x = {}
        for i in v:
            try:
                x[i.name] = u'%s' % i.value
            except:
                x[i.name] = u''
        return x
    