from django.db import models
from help.utils import unslugify
from django.core.exceptions import ObjectDoesNotExist

class HelpManager(models.Manager):
    
    def create_default(self, slug, app_label=""):
        title = unslugify(slug)
        return self.create(title=title, slug=slug, app_label=app_label)
    
    def _get_help_slug_from_url(self, url):
        """returns a tuple (slug, app_label) """
        #FIXME: make use of urlcrawler
        return "testslug", "help"
    
    def _get_help_object(self, slug, app_label=""):
        """
        returns `Help` object according to slug and app_label
        or None if it does not exists
        """
        
        qs = self.filter(slug=slug)
        if app_label:
            qs = qs.filter(app_label=app_label)
        
        try:
            obj = qs.get()
        except ObjectDoesNotExist:
            obj = None
        return obj

    def get_help_object(self, url):        
        slug, app =  self._get_help_slug_from_url(url)
        obj = self._get_help_object(slug, app)
        return obj
        
class Help(models.Model):
    slug = models.SlugField(max_length=1023)
    app_label = models.CharField(max_length=1023, null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    
    objects = HelpManager()
    
    @models.permalink
    def get_absolute_url(self):
        if self.app_label:
            return ('show_help_for_app', [str(self.slug), str(self.app_label)])
        else:
            return ('show_help', [str(self.slug)])
    
    class Meta:
        unique_together = ('slug', 'app_label')
