from django.conf.urls.defaults import *

urlpatterns = patterns('help.views',
    #TODO: fix slug regexps 
    url(r'(?P<slug>[-\w]+)/(?P<app_label>\w+)/$', 'show_help', name='show_help_for_app'),
    url(r'(?P<slug>[-\w]+)/$', 'show_help', name='show_help'),
    
)
