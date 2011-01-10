# -*- coding: utf-8 -*-
from apps.media.documents import File
from apps.social.documents import User

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in User.objects:
            if user.avatar:
                print user
                avatar = user.avatar
                avatar.type = 'avatar'
                avatar.save()

                for old_label, new_label in (
                    ('200x200', 'avatar_midi.png'),
                    ('60x60', 'avatar_mini.png'),
                    ('47x47', 'avatar_micro.png'),
                    ):
                    try:
                        derivative = avatar.modifications[old_label]
                    except File.DerivativeNotFound:
                        print old_label, 'not found'
                        continue
                    derivative.transformation = new_label
                    derivative.save()
