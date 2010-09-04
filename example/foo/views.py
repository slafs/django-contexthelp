from django.views.generic.simple import direct_to_template
from foo.models import Bar

def test_view(request): 
    """this docstring should be available in `test_view` help object"""
    return direct_to_template(request, "foo/test.html", 
                              { 'test' : "Check thizz out" })
    
def test_view2(request, argument):
    """this docstring should be also available but in `test_view2` help object"""
    
    qs = Bar.objects.filter(f1=argument)

    return direct_to_template(request, "foo/test2.html", 
                              { 'test_list' : qs })
