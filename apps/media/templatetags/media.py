# -*- coding: utf-8 -*-
from django import template
from django.template import TemplateSyntaxError, Node
from django.core.urlresolvers import reverse, NoReverseMatch

register = template.Library()

class MediaURLNode(Node):
    def __init__(self, file_obj, transformation_name):
        self.file_obj = file_obj
        self.transformation_name = transformation_name

    def render(self, context):
        return reverse('media:file_view',
                       kwargs=dict(file_id=str(context.get(self.file_obj).id),
                                   transformation_name=self.transformation_name))


@register.tag
def media_url(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                                  " file_object, transformation_name" % bits[0])

    file_obj = bits[1]
    transformation_name = bits[2]

    return MediaURLNode(file_obj, transformation_name)
