from help.models import Help
from django.contrib import admin

class HelpAdmin(admin.ModelAdmin):
    list_display=('slug', 'app_label', 'title')
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ('app_label',)
    
admin.site.register(Help, HelpAdmin)
