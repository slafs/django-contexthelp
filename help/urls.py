from django.conf.urls.defaults import *

urlpatterns = patterns('help.views',
    url(r'(?P<help_id>\d+)/$', 'show_help', name='show_help'),    
    url(r'(?P<slug>[-\w]+)/(?P<module_label>[-\w]+)/(?P<app_label>[-\w]+)/$', 
        'show_help', name='show_help_for_slug_module_and_app'),    
    url(r'(?P<slug>[-\w]+)/(?P<module_label>[-\w]+)/$', 'show_help', name='show_help_for_slug_and_module'),    
    url(r'(?P<slug>[-\w]+)/$', 'show_help', name='show_help_for_slug'),    
)
