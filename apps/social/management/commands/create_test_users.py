import sys
import random
import os


from django.test.client import Client
from django.contrib.webdesign import lorem_ipsum


from django.core.management.base import BaseCommand, CommandError
from apps.social import documents
from apps.user_messages.documents import Message
from apps.friends.documents import FriendshipOffer, UserFriends
import re
from django.core.urlresolvers import reverse
from apps.utils.test import patch_settings

class Command(BaseCommand):
    args = '[<number_of_users>]'
    help = ('creates number (10 by default) of test users with random'
        'friendship and messages')

    def handle(self, *args, **options):
        num = int(args and args[0] or 10)
        with_ava = len(args) > 1

        documents.User.objects.delete()
        Message.objects.delete()
        FriendshipOffer.objects.delete()
        UserFriends.objects.delete()

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
        print
        for i in xrange(num):
            if not i % (num/10 or 10):
                print  '\rusers creation %002d%%' % (i*100/num),
                sys.stdout.flush()
            if with_ava:
                if faces[i].find('/female/')!=-1:
                    name = random.choice(('iren', 'mary', 'ann',))
                else:
                    name = random.choice(('den', 'pete', 'serge', 'ivan', 'vladimir'))
            else:
                name = random.choice(('den', 'pete', 'serge', 'iren', 'mary',
                                  'dude', 'ivan', 'vladimir'))

            username = '%s%s' % (name, i)

            acc = documents.User.create_user(username=username,
                                      password='123')
            acc.save()
            if with_ava:
                client = Client()
                client.login(username=username, password='123')
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
