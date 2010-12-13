"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse

from help.models import Help
from help.utils import unslugify

class SimpleTest(TestCase):
    
    def test_unslug(self):
        slug = "some-weird-slug-2"
        shouldbe = "Some Weird Slug 2"
        
        unslug = unslugify(slug)
        self.failUnlessEqual(unslug, shouldbe)
    
    def test_simple_help(self):
        """
        test basic additions of help objects
        and test the views
        """
        testslug = "some-weird-slug"
        testmodule = "help-views"
        
        h, created = Help.objects.create_default(slug=testslug, module_label=testmodule)
        shouldbe_title = "Help Views Some Weird Slug"
        self.failUnlessEqual(shouldbe_title, h.title)
        
        help_url = reverse("show_help_for_slug_and_module", args=[testslug, testmodule])
        r = self.client.get(help_url, {})
        self.assertEqual(r.status_code, 200)

        help_url = reverse("show_help_for_slug", args=[testslug])
        r = self.client.get(help_url, {})
        self.assertEqual(r.status_code, 200)
        
        testslug = "some another weird slug"
        testmodule = "help views"
        testname = "help_2"
        
        h, created = Help.objects.create_default(slug=testslug, module_label=testmodule, url_name=testname)

        shouldbe_title = "Help 2 Help Views Some Another Weird Slug"
        self.failUnlessEqual(shouldbe_title, h.title)
        
        help_url = reverse("show_help_for_slug_module_and_app", args=['some-another-weird-slug', 'help-views', 'help2'])
        r = self.client.get(help_url, {})
        self.assertEqual(r.status_code, 200)

        help_url = reverse("show_help_for_slug", args=['some-another-weird-slug'])
        r = self.client.get(help_url, {})
        self.assertEqual(r.status_code, 200)
        
