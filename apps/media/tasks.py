# -*- coding: utf-8 -*-
from celery.decorators import task
from documents import File


@task()
def apply_file_transformations(source_id, *transformations):
    file = File.objects.get(id=source_id)
    file.apply_transformations(*transformations)
