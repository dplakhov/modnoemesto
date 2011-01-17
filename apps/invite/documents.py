# -*- coding: utf-8 -*-
from datetime import datetime
from apps.utils.mail import send_mail

from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from mongoengine.document import Document
from mongoengine.fields import ReferenceField, StringField
from mongoengine.fields import BooleanField, DateTimeField

class Invite(Document):
    sender = ReferenceField('User')

    creation_time = DateTimeField(default=datetime.now)
    registration_time = DateTimeField()
    activation_time = DateTimeField()

    recipient = ReferenceField('User')

    recipient_email = StringField()
    recipient_name = StringField()
    recipient_active = BooleanField(default=False)

    def send(self):
        email_body = render_to_string('emails/invite.txt',
                dict(
                        invite=self,
                        SITE_DOMAIN=settings.SITE_DOMAIN,
                     ))

        #if settings.DEBUG:
        #    print email_body

        if settings.SEND_EMAILS:
            send_mail(_('Site invite'), email_body,
            settings.ROBOT_EMAIL_ADDRESS, (self.recipient_email,),
            fail_silently=True)

    def register(self, user):
        self.registration_time = datetime.now()
        self.recipient = user
        self.save()

    def on_activate(self):
        self.activation_time = datetime.now()
        self.recipient_active = True
        self.save()

    @classmethod
    def invitee_count(cls, sender):
        return cls.objects(sender=sender,
                           recipient_active=True,
                           ).count()

    @classmethod
    def invites_count(cls, sender):
        return cls.objects(sender=sender).count()

