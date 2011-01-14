# -*- coding: utf-8 -*-

from datetime import datetime
import logging

from mongoengine import Document
from mongoengine import ReferenceField
from mongoengine import DateTimeField
from mongoengine import StringField

from django.core.mail import send_mass_mail
from django.conf import settings
from django.dispatch import dispatcher

from apps.social.documents import Profile
from apps.news import signals


class News(Document):
    title = StringField(max_length=128, required=True)
    text = StringField(required=True)
    preview_text = StringField(required=True)
    author = ReferenceField('User')
    ctime = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        super(News, self).save(*args, **kwargs)
        signals.news_post_save.send(self)

    meta = {
        'ordering': [
            '-ctime',
        ]
    }


def send_emails(article):
    profiles = Profile.objects.filter(get_news=True)

    subject = u"Новости с сайта %s: %s" % (
        settings.SITE_DOMAIN,
        article.title
    )
    message = article.text
    sender = settings.ROBOT_EMAIL_ADDRESS

    messages = []
    for profile in profiles:
        recipient = profile.user.email
        messages.append((subject, message, sender, [recipient]))

    send_mass_mail(messages)
#    except News.DoesNotExist, News.MultipleObjectsReturned:
#        logging.error("Error: news don't sent to user")


def send_notificaton(signal, sender, **kwargs):
    send_emails(sender)


signals.news_post_save.connect(send_notificaton)


