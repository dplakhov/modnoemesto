# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from apps.cam.documents import Camera, CameraTag


class Command(BaseCommand):
    def handle(self, *args, **options):
        tags = [u'Бар',
                u'Ресторан',
                u'Кинотеатр',
                u'Клуб',
                u'Квартира']
        for name in tags:
            CameraTag(name=name).save()
        tag = CameraTag(name=u'Личная', count=Camera.objects.count())
        tag.save()
        for camera in Camera.objects:
            camera.tags = [tag,]
            camera.save()