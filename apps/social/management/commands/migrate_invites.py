# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from apps.social.documents import User, Profile, Invite

class Command(BaseCommand):

    def handle(self, *args, **options):
        for profile in Profile.objects(inviter__exists=True):
            user = profile.user
            inviter = profile.inviter
            is_active = profile.is_active
            
            print inviter, '=>', user, is_active

            invite = Invite(sender=inviter)
            invite.register(user)
            if is_active:
                invite.on_activate()

