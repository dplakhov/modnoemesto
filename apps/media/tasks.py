# -*- coding: utf-8 -*-
from celery.decorators import task
from files import ImageFile


@task()
def apply_image_transformations(source_id, *transformations):
    file = ImageFile.objects.get(id=source_id)
    file.apply_transformations(*transformations)
