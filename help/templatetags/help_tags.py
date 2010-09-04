from django import template
from django.core.exceptions import ImproperlyConfigured

from help.models import Help 
from help.utils import get_path_from_context, slug_those
from django.template.defaultfilters import slugify

register = template.Library()

class BaseHelpNode(template.Node):
    
    def __init__(self, slug=None, module_label=None, app_label=None, as_var=None):
        self.slug = slug
        self.module_label = module_label
        self.app_label = app_label
        self.as_var = as_var
        
    def handle_token(cls, parser, token):
        """Class method to parse tag and return a Node."""
        orig_tokens = token.contents.split()
        tl = len(orig_tokens) 
        if tl == 1:
            return cls(None, None, None, None)
        if tl > 2:
            if orig_tokens[-2] != 'as':
                raise template.TemplateSyntaxError("Second argument from the end in %r must be 'as'" 
                                                   % orig_tokens[0])
            
            tokens = []
            for i, token in enumerate(orig_tokens):
                value = ""
                if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
                    value = token[1:-1]
                elif i > 0 and i < tl - 1: # change only inside tokens 
                    value = template.Variable(token)
                else: 
                    value = token
                tokens.append(value)
            
            if tl == 3:
                return cls(None, None, None, tokens[2])
            elif tl == 4:
                return cls(tokens[1], None, None, tokens[3])                
            elif tl == 5:
                return cls(tokens[1], tokens[2], None, tokens[4])            
            elif tl == 6:
                return cls(tokens[1], tokens[2], tokens[3], tokens[5])
            else:
                raise template.TemplateSyntaxError('To many arguments of "%r".' % orig_tokens[0])
        else:
            raise template.TemplateSyntaxError('To few arguments of "%r".' % orig_tokens[0])

    handle_token = classmethod(handle_token)

    def obtain_help_link(self, context, slug=None, module_label=None, app_label=None):
        raise NotImplementedError
    
    def render(self, context):
        to_resolve = [self.slug, self.module_label, self.app_label]
        for i, v in enumerate(to_resolve):
            if isinstance(v, template.Variable):
                to_resolve[i] = v.resolve(context)
            elif v is None:
                to_resolve[i] = ""

        help_link = self.obtain_help_link(context, *to_resolve)
        
        if self.as_var is None:
            return help_link
        else:
            context[self.as_var] = help_link
        return ''

class HelpLinkNode(BaseHelpNode):
    
    def obtain_help_link(self, context, slug="", module_label="", app_label=""):
        help_obj = None

        if not slug:
            current_link = get_path_from_context(context)   
            help_obj = Help.objects.get_help_object_from_url(current_link)
        else:
            slug, module_label, app_label = slug_those(slug, module_label, app_label)
            help_obj = Help.objects.get_help_object(slug, module_label=module_label, 
                                                    app_label=app_label)
            
        help_link = ""
        if help_obj is not None:
            help_link = help_obj.get_absolute_url()
        
        return help_link    

def get_help_link(parser, token):
    ''' TODO: Make docsting'''
    return HelpLinkNode.handle_token(parser, token)

register.tag(get_help_link)

def render_help(context, slug="", module_label="", app_label=""):
    
    help_obj = None
    
    if not slug:
        current_link = get_path_from_context(context) 
        help_obj = Help.objects.get_help_object_from_url(current_link)
    else:
        slug, module_label, app_label = slug_those(slug, module_label, app_label)
        help_obj = Help.objects.get_help_object(slug, module_label=module_label, 
                                                app_label=app_label)
    
    return { 'object' : help_obj }
    
register.inclusion_tag('help/display_help.html', takes_context=True)(render_help)