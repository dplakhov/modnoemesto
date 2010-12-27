# -*- coding: utf-8 -*-
from apps.cam.documents import Camera
from apps.media.documents import File

from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):
        for cam in Camera.objects:
            if cam.screen:
                for old_label, new_label in (
                    ('screen_515x330.png','camera_screen_full.png'),
                    ('screen_170x109.png','camera_screen_normal.png'),
                    ('screen_80x51.png','camera_screen_mini.png'),
                ):
                    try:
                        derivative = cam.screen.modifications[old_label]
                    except File.DerivativeNotFound:
                        continue
                    derivative.transformation = new_label
                    derivative.save()