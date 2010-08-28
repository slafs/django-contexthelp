from django.views.generic.simple import direct_to_template
from foo.models import Bar

def test_view(request): 
    return direct_to_template(request, "foo/test.html", 
                              { 'test' : "Check thizz out" })
    
def test_view2(request, argument):
    qs = Bar.objects.filter(f1=argument)
    
    return direct_to_template(request, "foo/test2.html", 
                              { 'test_list' : qs })
 