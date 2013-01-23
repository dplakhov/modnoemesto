# -*- coding: utf-8 -*-
from django.template.loader import BaseLoader
from django.template import TemplateDoesNotExist

from .thread_locals import _thread_locals

class Loader(BaseLoader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        try:
            theme = getattr(_thread_locals, 'current_theme', None)
            if theme:
                display_name = 'theme:%s:%s:%s' % (
                    theme.name,
                    theme.id,
                    template_name
                )
                
                template = theme.templates[template_name]
                return (template.content, display_name)
        except:
            pass
        raise TemplateDoesNotExist(template_name)

    load_template_source.is_usable = True

