# -*- coding: utf-8 -*-
from apps.cam.documents import Camera
from apps.media.documents import File

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        for cam in Camera.objects:
            if cam.screen:
                print cam.name
                for old_label, new_label in (
                    ('515x330','camera_screen_full.png'),
                    ('170x109','camera_screen_normal.png'),
                    ('80x51','camera_screen_mini.png'),
                    ):
                    try:
                        derivative = cam.screen.modifications[old_label]
                    except File.DerivativeNotFound:
                        print old_label, 'not found'
                        continue
                    derivative.transformation = new_label
                    derivative.save()
