# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from apps.social.documents import User

class Command(BaseCommand):
    help = ('creates number (10 by default) of test users with random'
        'friendship and messages')

    def handle(self, *args, **options):
        for user in User.objects().order_by('-date_joined'):
            print user.email, '\t', user.date_joined

