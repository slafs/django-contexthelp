"""module with all helper functions of django-help app"""
from django.core.exceptions import ImproperlyConfigured

import string
from django.template.defaultfilters import title, slugify

table = string.maketrans(string.punctuation, " "*len(string.punctuation))

def unslugify(slug):
    """NOTE: this is obviously NOT intendent to be the reverse function of slugify"""
    t = str(slug).translate(table)
    return title(t)

def slug_those(*args):
    l = []
    for arg in args:
        l.append(slugify(arg))
    return l


def get_path_from_context(context):
    req = context.get('request')
    if req is None:
        raise ImproperlyConfigured("There's is no request in context. "
                                   "Add 'django.core.context_processors.request' "
                                   "to TEMPLATE_CONTEXT_PROCESSORS in your settings")
    
    current_link = req.META.get('PATH_INFO')

    return current_link

def create_title(*args):
    """Helper function to create "pretty" title"""
    return " ".join([unslugify(arg) for arg in reversed(args) if arg])
