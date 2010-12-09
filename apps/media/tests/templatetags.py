# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.template import Context, Template
from django.conf import settings
from django.template import TemplateSyntaxError


from .common import file_path, create_file

class TemplatetagsTest(TestCase):
    def test_media_url_file_exists(self):
        file = create_file()
        file.apply_transformations()
        url = reverse('media:file_view', kwargs=dict(file_id=file.id,
                                                     transformation_name='thumb.png'))
        template = Template('''{% load media %}{% media_url file thumb.png %}''')
        context = Context(dict(file=file))
        rendered = template.render(context)
        self.failUnlessEqual(url, rendered)

    def test_media_url_file_not_exists(self):
        file_name = '_test_image.png'
        template = Template('{% load media %}{% media_url file ' + file_name + ' %}')
        context = Context(dict(file=None))
        rendered = template.render(context)
        self.failUnlessEqual('%snotfound/%s' % (settings.MEDIA_URL, file_name), rendered)

    def test_media_url_404_file_not_exists(self):
        file_name = 'jsdfkjhdfsksjdfh.png'
        template = Template('{% load media %}{% media_url file ' + file_name + ' %}')
        context = Context(dict(file=None))
        self.failUnlessRaises(TemplateSyntaxError, template.render, context)



    def test_media_url_file_invalid(self):
        file_name = '_test_image.png'
        template = Template('{% load media %}{% media_url file ' + file_name + ' %}')
        context = Context(dict(file=template))
        self.failUnlessRaises(TemplateSyntaxError, template.render, context)
        
