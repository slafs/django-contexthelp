"""module with all helper functions of django-help app"""
from django.core.exceptions import ImproperlyConfigured

import re
import string
from django.template.defaultfilters import title, slugify

table = string.maketrans(string.punctuation, " "*len(string.punctuation))

def unslugify(slug):
    """NOTE: this is obviously NOT intendent to be the reverse function of slugify"""
    return title(slug.translate(table))

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

def create_title(slug, module_label="", app_label=""):
    """Helper function to create pretty title"""
    title = ""
    title_strings = ("%(app)s %(mod)s %(slug)s", 
                     "%(mod)s %(slug)s",
                     "%(app)s %(slug)s",
                     "%(slug)s")
    title_f = lambda format: unslugify(format % 
                                  {'app' : app_label, 'mod' : module_label, 'slug' : slug })
    if app_label and module_label:
        title = title_f(title_strings[0])
    elif not app_label and module_label:
        title = title_f(title_strings[1])
    elif app_label and not module_label:
        title = title_f(title_strings[2])
    else:
        title = title_f(title_strings[3])

    return title