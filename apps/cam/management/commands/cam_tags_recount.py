# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from apps.cam.documents import Camera, CameraTag
from mongoengine.queryset import OperationError


class Command(BaseCommand):
    def handle(self, *args, **options):
        for tag in CameraTag.objects:
            tag.count = Camera.objects(tags=tag).count()
            tag.save()