# -*- coding: utf-8 -*-

import sys
import random
import os
import re

from django.test.client import Client
from django.contrib.webdesign import lorem_ipsum


from django.core.management.base import BaseCommand, CommandError
from apps.social import documents
from apps.user_messages.documents import Message
from apps.friends.documents import FriendshipOffer, UserFriends
from apps.groups.documents import GroupUser

from django.core.urlresolvers import reverse
from apps.utils.test import patch_settings

class Command(BaseCommand):
    args = '[<number_of_users>]'
    help = ('creates number (10 by default) of test users with random'
        'friendship and messages')

    def handle(self, *args, **options):
        num = int(args and args[0] or 10)
        with_ava = len(args) > 1

        for type in (
            documents.User,
            Message,
            FriendshipOffer,
            UserFriends,
            GroupUser,
        ):
            type.objects.delete()

        if with_ava:
            if not os.path.exists('faces94'):
                raise CommandError('faces database not exists, do\n'
                   'wget http://cswww.essex.ac.uk/mv/allfaces/faces94.zip && unzip faces94.zip')

            faces = []

            def visit(arg, dirname, names):
                if len(re.split('/', dirname)) != 3:
                    return
                faces.append(os.path.join(dirname, random.choice(names)))
                
            os.path.walk('faces94', visit, None)
            random.shuffle(faces)
            
        # creating accounts
        male_first_names = u'''
        Сергей
        Александр
        Дмитрий
        Андрей
        Артур
        Игорь
        Армен
        Алексей
        Григорий
        '''.split()

        female_first_names = u'''
        Анна
        Анастасия
        Риана
        Елена
        Мария
        Дарина
        Кристина
        Марина
        Ангелина
        Полина
        '''.split()

        male_last_names = u'''
        Смирнов
        Иванов
        Кузнецов
        Соколов
        Попов
        Лебедев
        Козлов
        Новиков
        Морозов
        Петров
        Волков
        Соловьёв
        Васильев
        Зайцев
        Павлов
        Семёнов
        Голубев
        Виноградов
        Богданов
        Воробьёв
        Фёдоров
        Михайлов
        Беляев
        Тарасов
        '''.split()

        female_last_names = [u'%sа' % x for x in male_last_names]

        male_names = (male_first_names, male_last_names)
        female_names = (female_first_names, female_last_names)

        print
        for i in xrange(num):
            if not i % (num/10 or 10):
                print  '\rusers creation %002d%%' % (i*100/num)
                sys.stdout.flush()
            if with_ava:
                if faces[i].find('/female/')!=-1:
                    names = female_names
                else:
                    names = male_names
            else:
                names = random.choice((male_names, female_names))

            first_name = random.choice(names[0])
            last_name = random.choice(names[1])

            email='%d@ya.ru' % i

            acc = documents.User.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password='123',
                    is_superuser=bool(not i)
                    )
            acc.save()
            if with_ava:
                client = Client()
                client.login(email=email, password='123')
                file = open(faces[i])
                with patch_settings(TASKS_ENABLED={}):
                    client.post(reverse('social:avatar_edit'), {'file': file})

        print  '\rusers creation 100%'
        # friending & messaging
        print
        for i in xrange(num):
            max_friends_count = random.randint(0, num % 25 + 25)
            friends_numbers = set([ random.randint(0, num-1) for _ in
                            xrange(max_friends_count) ]).difference(set([i]))
            this_user = documents.User.objects().order_by('username')[i]

            for fn in friends_numbers:
                friend = documents.User.objects().order_by('username')[fn]
                #this_user.reload()
                this_user.friends.offers.send(friend)
                random.randint(0,3) and friend.friends.offers.send(this_user) # ~66%

            max_msg_sndrs_count = random.randint(0, num)
            msg_sndrs_numbers = set([ random.randint(0, num-1) for _ in
                            xrange(max_msg_sndrs_count) ]).difference(set([i]))

            for sndr_num in msg_sndrs_numbers:
                messages_count = random.randint(0, 3)

                sndr = documents.User.objects().order_by('username'
                                                            )[sndr_num]
                for _ in xrange(messages_count):
                    Message.send(sndr, this_user, lorem_ipsum.paragraph())

            if not i % (num/10 or 10):
                print  '\rfriending and messaging %002d%%' % (i*100/num),
                sys.stdout.flush()
        print  '\rfriending and messaging 100%'
