from django.conf.urls.defaults import *

urlpatterns = patterns('foo.views',
    url(r'test/(?P<argument>[-\w]+)', 'test_view2', name="test_view2"),
    url(r'test/$', 'test_view', name="this_is_the_name"),
)
