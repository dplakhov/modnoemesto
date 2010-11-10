import sys
from django.core.management.base import BaseCommand, CommandError
from apps.social import documents

import random

class Command(BaseCommand):
    args = '[<number_of_users>]'
    help = ('creates number (10 by default) of test users with random'
        'friendship and messages')

    def handle(self, *args, **options):
        num = int(args and args[0] or 10)

        documents.Account.objects.delete()
        documents.Message.objects.delete()
        documents.FriendshipOffer.objects.delete()

        # creating accounts
        print
        for i in xrange(num):
            if not i % (num/10 or 10):
                print  '\rusers creation %002d%%' % (i*100/num),
                sys.stdout.flush()
            name = random.choice(('den', 'pete', 'serge', 'iren', 'mary',
                                  'dude', 'ivan', 'vladimir'))
            acc = documents.Account.create_user(username='%s%s' % (name, i),
                                      password='123')
            acc.save()
        print  '\rusers creation 100%'

        # friending & messaging
        print
        for i in xrange(num):
            max_friends_count = random.randint(0, num % 25 + 25)
            friends_numbers = set([ random.randint(0, num-1) for _ in
                            xrange(max_friends_count) ]).difference(set([i]))
            this_user = documents.Account.objects().order_by('username')[i]

            for fn in friends_numbers:
                friend = documents.Account.objects().order_by('username')[fn]
                #this_user.reload()
                this_user.friend(friend)
                random.randint(0,3) and friend.friend(this_user) # ~66%

            max_msg_sndrs_count = random.randint(0, num)
            msg_sndrs_numbers = set([ random.randint(0, num-1) for _ in
                            xrange(max_msg_sndrs_count) ]).difference(set([i]))

            for sndr_num in msg_sndrs_numbers:
                messages_count = random.randint(0, 3)

                sndr = documents.Account.objects().order_by('username'
                                                            )[sndr_num]
                for _ in xrange(messages_count):

                    text = ' '.join(random.choice(('hey', 'hello', 'what',
                                                   'test', 'text', 'maybe',
                                                   'joke', 'err', 'ohno!',
                                                   'damn', 'cool'))
                                  for i in xrange(5, 25))

                    sndr.send_message(text, this_user)

            if not i % (num/10 or 10):
                print  '\rfriending and messaging %002d%%' % (i*100/num),
                sys.stdout.flush()
        print  '\rfriending and messaging 100%'
