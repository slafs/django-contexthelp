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
        shouldbe = "Some weird slug 2"
        
        unslug = unslugify(slug)
        self.failUnlessEqual(unslug, shouldbe)
    
    def test_simple_help(self):
        """
        test basic additions of help objects
        and test the views
        """
        testslug = "some-weird-slug"
        testapp = "help"
        shouldbe_title = "Some weird slug"
        
        h = Help.objects.create_default(slug=testslug, app_label=testapp)
        self.failUnlessEqual(shouldbe_title, h.title)
        
        help_url = reverse("show_help_for_app", args=[testslug, testapp])
        r = self.client.get(help_url, {})
        self.assertEqual(r.status_code, 200)

        #there shouldn't be any entry with testslug and without testapp
        help_url = reverse("show_help", args=[testslug])
        r = self.client.get(help_url, {})
        self.assertEqual(r.status_code, 404)
        
        testslug = "some-another-weird-slug"
        testapp = "help_2"
        shouldbe_title = "Some another weird slug"
        
        h = Help.objects.create_default(slug=testslug)
        self.failUnlessEqual(shouldbe_title, h.title)
        
        #there shouldn't be any entry with testslug and with testapp
        help_url = reverse("show_help_for_app", args=[testslug, testapp])
        r = self.client.get(help_url, {})
        self.assertEqual(r.status_code, 404)

        help_url = reverse("show_help", args=[testslug])
        r = self.client.get(help_url, {})
        self.assertEqual(r.status_code, 200)
        
