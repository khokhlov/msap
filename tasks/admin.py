from django.contrib import admin


from .models import *

admin.site.register(BaseTask)
admin.site.register(TextTask)
