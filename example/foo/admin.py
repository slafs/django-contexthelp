from django.contrib import admin
from foo.models import Bar

class BarAdmin(admin.ModelAdmin):
    list_display = ('f1',)

admin.site.register(Bar, BarAdmin)