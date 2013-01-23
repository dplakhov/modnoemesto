# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from apps.groups.documents import Group, GroupUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        for group in Group.objects:
            group.count_members = GroupUser.objects(group=group, status=GroupUser.STATUS.ACTIVE).count()
            group.save()
            print "%s: %i" %(group.name, group.count_members)