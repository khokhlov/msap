from django.contrib import admin

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


from reversion_compare.helpers import patch_admin

from .models import *

class GeneratedDocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'active', 'created', 'modified']
    list_filter = ('active', )
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('template_info',)

class GeneratedDocumentProcessorAdmin(admin.ModelAdmin):
    list_display = ['name', 'clazz']

admin.site.register(GeneratedDocumentTemplate, GeneratedDocumentTemplateAdmin)
admin.site.register(GeneratedDocumentProcessor, GeneratedDocumentProcessorAdmin)

patch_admin(GeneratedDocumentTemplate)
