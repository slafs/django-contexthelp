from django.views.generic.list_detail import object_detail
from help.models import Help

def show_help(request, help_id=None, template_name=None, 
              slug=None, module_label=None, app_label=None,
              **object_detail_kwargs):
    
    qs = Help.objects.all()

    if module_label:
        qs = qs.filter(module_label=module_label)
    if app_label:
        qs = qs.filter(app_label=app_label)
        
    if not template_name:
        template_name = "help/show_help.html"
    
    return object_detail(request, qs, help_id, slug=slug, template_name=template_name, 
                         template_name_field="template_name", **object_detail_kwargs)
    