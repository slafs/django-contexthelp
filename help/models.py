from django.db import models
from help.utils import unslugify, create_title, slug_those
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import get_resolver, get_urlconf, Resolver404,\
    reverse, RegexURLPattern, RegexURLResolver, resolve
from django.db.utils import IntegrityError
from django.template.defaultfilters import slugify

from django.utils.translation import ugettext_lazy as _

class HelpManager(models.Manager):
    
    
    def create_default(self, slug=None, module_label=None, 
                           url_name=None, **kwargs):
        
        title = create_title(slug, module_label, url_name)
        
        kwargs.update({ 'title' : title })
        
        print 'probuje', slug, module_label, url_name
        return self.get_or_create(slug=slug, module_label=module_label, 
                           url_name=url_name, defaults=kwargs)
    
    def _get_resolver(self):
        return get_resolver(get_urlconf())
    
    def _handle_urlpattern(self, urlpatterns, already_patterns):
        '''returns a (slug, module_label, url_name) from RegexURLPattern
        takes an iterable of urlpatterns
        This method flattens the urlpatterns and fills out the _patterns attr
        maybe this is useless but i couldn't find 
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

    def _get_help_slugs_from_pattern(self, pattern):
        if type(pattern) == RegexURLPattern:
            f = pattern.callback
        else:
            f = pattern[0]
        slug = slugify( getattr(f, "__name__", "") )
        module_label = slugify( getattr(f, "__module__", "") )
        url_name = slugify( getattr(pattern, "url_name", "") )
        if not url_name:
            print 'nie ma url_name'
            url_name = module_label + slug
        return slug, module_label, url_name

    
    def create_help_objects_from_urls(self, only_for_apps=None, exclude_apps=None):
        '''creates help objects by iterating over your url_patterns.
        It generates one help object per url_name
        `only_for_apps` and `exclude_apps` are tuples of app names'''
        
        if only_for_apps and exclude_apps:
            raise AttributeError("Only one tuple of 'only_for_apps' and 'exclude_apps' "
                                 "can be provided.")
            
        resolver = self._get_resolver()
        result = self._handle_urlpattern(resolver.url_patterns, [])

        for pat in result:
            slug, module_label, url_name, content = "", "", "", ""
            slug, module_label, url_name = self._get_help_slugs_from_pattern(pat)
            print type(pat)
            print dir(pat)
            
            f = pat.callback            
            content = f.__doc__ 
            kwargs = {} 
            kwargs.update({ 'content' : content })
            
            self.create_default(slug, module_label, url_name, **kwargs)
    
    
    def _get_help_slugs_from_url(self, url):
        """returns a tuple (slug, module_label, url_name) for a given url (path)""" 
        #TODO: figure out how to get url_name from resolve
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
        self.module_label = slugify(self.module_label)
        self.url_name = slugify(self.url_name)
        super(Help, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        if self.help_link:
            return self.help_link
        return reverse('show_help', args=[str(self.pk)])
    

