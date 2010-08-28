from django import template
from django.core.exceptions import ImproperlyConfigured

from help.models import Help 

register = template.Library()

def help_link(context):
    
    print dir(context), context
    req = context.get('request')
    if req is None:
        raise ImproperlyConfigured("add 'django.core.context_processors.request'"
                                   "to TEMPLATE_CONTEXT_PROCESSORS in your settings")
    current_link = req.META.get('PATH_INFO')
    
    help_obj = Help.objects.get_help_object(current_link)
    
    help_link = "#"
    if help_obj is not None:
        help_link = help_obj.get_absolute_url()
    
    return { 'help_link' : help_link }
    
register.inclusion_tag('help/help_link.html', takes_context=True)(help_link)
