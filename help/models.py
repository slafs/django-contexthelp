from django.db import models
from help.utils import unslugify, create_title, slug_those
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import get_resolver, get_urlconf, Resolver404,\
    reverse, RegexURLPattern, RegexURLResolver, resolve
from django.db.utils import IntegrityError
from django.template.defaultfilters import slugify

from django.utils.translation import ugettext_lazy as _

class HelpManager(models.Manager):
    
    def _get_resolver(self):
        return get_resolver(get_urlconf())
    
    def _handle_urlpattern(self, urlpatterns, already_patterns):
        '''returns a (slug, module_label, url_name) from RegexURLPattern
        takes an iterable of urlpatterns
        This method flattens the urlpatterns
        NOTE: probably this is too much overhead but i couldn't find 
        any applicable method in Django
        '''
        for pat in urlpatterns:
            if isinstance(pat, RegexURLPattern):
                already_patterns.append(pat)
            elif isinstance(pat, RegexURLResolver):
                self._handle_urlpattern(pat.url_patterns, already_patterns)      
            else:
                pass
        return already_patterns
    
    def url_patterns(self):
        '''property that holds all url_patterns nicely flattened'''
        if getattr(self, '_url_patterns', False):
            return self._url_patterns
        
        resolver = self._get_resolver()
        self._url_patterns = self._handle_urlpattern(resolver.url_patterns, [])
        return self._url_patterns
    
    url_patterns = property( url_patterns )
    
    def create_default(self, slug=None, module_label=None, 
                           url_name=None, **kwargs):
        
        title = create_title(slug, module_label, url_name)
        
        kwargs.update({ 'title' : title })
        
        print 'probuje', slug, module_label, url_name
        return self.get_or_create(slug=slug, module_label=module_label, 
                           url_name=url_name, defaults=kwargs)

    def _dumb_get_url_name(self, pattern):
        '''this imitates the Django 1.3 functionality
        and returns the url_name of a given pattern (tuple returned by `resolve`)
        '''
        f, args, kwargs = pattern
        path = reverse(f, args=args, kwargs=kwargs)
        if path.endswith('/'):
            path = path[:-1] # not sure why I have to do this, but it works :)
        for r in self.url_patterns:
            result = r.resolve(path)
            if result is not None:
                return r.name
        return ""
        
    def _get_help_slugs_from_pattern(self, pattern):
        '''TODO: make compatible with Django 1.3'''
        if type(pattern) == RegexURLPattern:
            f = pattern.callback
            url_name =  getattr(pattern, "name", "") 
        else:
            # pattern is a tuple ( len(pattern) == 3 )
            f = pattern[0]
            url_name = self._dumb_get_url_name(pattern)
            
        slug =  getattr(f, "__name__", "") 
        module_label =  getattr(f, "__module__", "") 
        return slug, module_label, url_name

    
    def create_help_objects_from_urls(self, only_for_apps=None, exclude_apps=None):
        '''creates help objects by iterating over your url_patterns.
        It generates one help object per url_name
        `only_for_apps` and `exclude_apps` are tuples of app names'''
        
        if only_for_apps and exclude_apps:
            raise AttributeError("Only one tuple of 'only_for_apps' and 'exclude_apps' "
                                 "can be provided.")
            

        for pat in self.url_patterns:
            slug, module_label, url_name, content = "", "", "", ""
            slug, module_label, url_name = self._get_help_slugs_from_pattern(pat)
            
            
            f = pat.callback            
            content = f.__doc__ 
            kwargs = {} 
            kwargs.update({ 'content' : content })
            
            print slug, module_label, url_name
            self.create_default(slug, module_label, url_name, **kwargs)
    
    
    def _get_help_slugs_from_url(self, url):
        """returns a tuple (slug, module_label, url_name) for a given url (path)""" 
        #TODO: figure out how to get url_name from resolve
        print 'URL', url
        slug = ""
        module_label = ""
        url_name = ""
        resolver = self._get_resolver()
        
        try:
            resolved = resolver.resolve(url)
            slug, module_label, url_name = self._get_help_slugs_from_pattern(resolved)         
            print '_get_help_slugs_from_url', slug, module_label, url_name
        except Resolver404:
            pass
        
        return slug, module_label, url_name
    
    def get_help_object(self, *args):
        """
        returns `Help` object according to slug and module_label
        or None if it does not exists
        args:
            - slug
            - module_label
            - url_name 
        """
        slugged = slug_those(*args)
        slug, module_label, url_name = slugged
        
        qs = self.filter(slug=slug)
        if module_label:
            qs = qs.filter(module_label=module_label)
        if url_name:
            qs = qs.filter(url_name=url_name)
            
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

    # for future usage (since 1.3 I suppose)
    url_name = models.SlugField(max_length=1023, null=True, blank=True)
    
    title = models.CharField(max_length=3069)
    content = models.TextField(null=True, blank=True)
    
    template_name = models.CharField(max_length=1023, null=True, blank=True)
    duplicate_for = models.ForeignKey('self', related_name='duplicates', null=True, blank=True)
    help_link = models.URLField(max_length=1023, null=True, blank=True, verify_exists=False,
                                 help_text=_(u'''Link to provide an external help object (i.e. Sphinx doc url).'''))
    
    objects = HelpManager()

    class Meta:
        unique_together = ('slug', 'module_label', 'url_name')   

    def __unicode__(self):
        return u"%s" % self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.slug)
        if self.module_label is not None:
            self.module_label = slugify(self.module_label)
        if self.url_name is not None:
            self.url_name = slugify(self.url_name)
        super(Help, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        if self.help_link:
            return self.help_link
        return reverse('show_help', args=[str(self.pk)])
    

