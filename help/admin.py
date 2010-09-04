from help.models import Help
from django.contrib import admin

class HelpAdmin(admin.ModelAdmin):
    list_display=('slug', 'module_label', 'title')
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ('module_label',)
    
admin.site.register(Help, HelpAdmin)
