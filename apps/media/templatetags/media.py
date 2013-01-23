# -*- coding: utf-8 -*-
from django import template
from django.template import TemplateSyntaxError, Node
from django.core.urlresolvers import reverse, NoReverseMatch
from django.conf import settings


from ..documents import File
import os

register = template.Library()

class MediaURLNode(Node):
    def __init__(self, file_obj, transformation_name):
        self.file_obj = file_obj
        self.transformation_name = transformation_name

    def render(self, context):
        path = self.file_obj.split('.')
        file = context.get(path[0])
        if file:
            try:
                for obj in path[1:]:
                    file = getattr(file, obj)
            except AttributeError:
                file = None

        not_found_path = '%snotfound/%s'
        transformation_name = self.transformation_name
        if file:
            if not isinstance(file, File):
                raise TemplateSyntaxError(
                        "First argument is not File object or None")

            return reverse('media:file_view',
                           kwargs=dict(file_id=file.id,
                               transformation_name=transformation_name))

        else:
            url = '%snotfound/%s' % (settings.MEDIA_URL,
                self.transformation_name)

            if not os.path.exists(not_found_path % (settings.MEDIA_ROOT,
                                            transformation_name)):
                raise TemplateSyntaxError("Stub file for url '%s' not found"
                                          % url)
            return url


@register.tag
def media_url(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                                  " file_object of None, transformation_name" % bits[0])

    file_obj = bits[1]
    transformation_name = bits[2]

    return MediaURLNode(file_obj, transformation_name)
