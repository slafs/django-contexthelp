from django.db import models
from help.utils import unslugify, create_title, slug_those
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import get_resolver, get_urlconf, Resolver404
from django.db.utils import IntegrityError
from django.template.defaultfilters import slugify

from django.utils.translation import ugettext_lazy as _

class HelpManager(models.Manager):
    
    def create_default(self, slug, module_label="", app_label="", **kwargs):
        
        title = create_title(slug, module_label=module_label, app_label=app_label)
        
        return self.create(title=title, slug=slug, module_label=module_label, 
                           app_label=app_label, **kwargs)
    
    def _get_resolver(self):
        return get_resolver(get_urlconf())
    
    def create_help_objects_from_urls(self, only_for_apps=None, exclude_apps=None):
        '''creates help objects by iterating over your url_patterns.
        It generates one help object per view
        `only_for_apps` and `exclude_apps` are tuples of app names'''
        
        if only_for_apps and exclude_apps:
            raise AttributeError("Only one tuple of 'only_for_apps' and 'exclude_apps' "
                                 "can be provided.")
            
        resolver = self._get_resolver()
        url_patterns = resolver.url_patterns
        for pattern in url_patterns:
            
            app_label = pattern.app_name
            if not app_label: app_label = ""
            
            if app_label and only_for_apps and not app_label in only_for_apps:
                continue
            if app_label and exclude_apps and app_label in exclude_apps:
                continue
            
            for view, arg_tuple in pattern.reverse_dict.iteritems():
                slug = ""
                module_label = ""
                kwargs = {}
                if callable(view):
                    if hasattr(view, '__name__'):
                        slug = view.__name__
                        module_label = view.__module__
                    else:
                        slug = view.__class__.__name__
                        module_label = view.__class__.__module__
                        
                    if hasattr(view, '__doc__'):
                        kwargs.update({'content' : view.__doc__ }) 
                if slug:
                    print slug, module_label, app_label
                    try:
                        self.create_default(slug, module_label, app_label, **kwargs)
                    except IntegrityError:
                        pass
    
    def _get_help_slugs_from_url(self, url):
        """returns a tuple (slug, module_label, app_label) for a given url (path) 
        NOTE: for now app_label is always an empty string"""
        #TODO: figure out how to get app_label from resolve
        slug = ""
        module_label = ""
        app_label = ""
        resolver = self._get_resolver()
        
        try:
            resolved = resolver.resolve(url)
            f = resolved[0] 
            slug = slugify(f.__name__)
            module_label = slugify(f.__module__)
        except Resolver404:
            pass
        
        return slug, module_label, app_label
    
    def get_help_object(self, slug, module_label="", app_label=""):
        """
        returns `Help` object according to slug and module_label
        or None if it does not exists
        """
        slug, module_label, app_label = slug_those(slug, module_label, app_label)
        
        qs = self.filter(slug=slug)
        if module_label:
            qs = qs.filter(module_label=module_label)
        if app_label:
            qs = qs.filter(app_label=app_label)
            
        try:
            obj = qs.get()
        except ObjectDoesNotExist:
            obj = None
        return obj

    def get_help_object_from_url(self, url):        
        slug, module, app =  self._get_help_slugs_from_url(url)
        obj = self.get_help_object(slug, module, app)
        return obj
        
class Help(models.Model):
    #TODO: write some help texts
    slug = models.SlugField(max_length=1023)
    module_label = models.SlugField(max_length=1023, null=True, blank=True)

    # for future usage
    app_label = models.SlugField(max_length=1023, null=True, blank=True)
    
    title = models.CharField(max_length=3069)
    content = models.TextField(null=True, blank=True)
    
    template_name = models.CharField(max_length=1023, null=True, blank=True)
    duplicate_for = models.ForeignKey('self', related_name='duplicates', null=True, blank=True)
    help_link = models.CharField(max_length=1023, null=True, blank=True, 
                                 help_text=_(u'''Link to provide an external help object (i.e. Sphinx doc url).
It can be either Django url/view name or full "http://" url'''))
    
    objects = HelpManager()
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.slug)
        self.module_label = slugify(self.module_label)
        self.app_label = slugify(self.app_label)
        super(Help, self).save(*args, **kwargs)
    
    @models.permalink
    def get_absolute_url(self):
        return ('show_help', [str(self.pk)])
    
    def __unicode__(self):
        return u"%s" % self.title
    
    class Meta:
        unique_together = ('slug', 'module_label', 'app_label')
