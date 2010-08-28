from django.views.generic.list_detail import object_detail
from help.models import Help

def show_help(request, slug, app_label="", template_name="help/show_help.html", 
              **object_detail_kwargs):
    
    qs = Help.objects.filter(app_label=app_label)
    
    return object_detail(request, qs, slug=slug, template_name=template_name, 
                         **object_detail_kwargs)