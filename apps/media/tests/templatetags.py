# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.template import Context, Template

from .common import file_path, create_file

class TemplatetagsTest(TestCase):
    def test_media_url(self):
        file = create_file()
        file.apply_transformations()
        url = reverse('media:file_view', kwargs=dict(file_id=file.id,
                                                     transformation_name='thumb.png'))
        template = Template('''{% load media %}{% media_url file thumb.png %}''')
        context = Context(dict(file=file))
        rendered = template.render(context)
        self.failUnlessEqual(url, rendered)
