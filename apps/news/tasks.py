# -*- coding: utf-8 -*-
from celery.decorators import task
from .documents import News
from django.core.mail import send_mass_mail
from django.conf import settings
from apps.social.documents import Profile
import logging


@task()
def send_notification(id):
    try:
        article = News.objects.get(pk=id)
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
    except News.DoesNotExist, News.MultipleObjectsReturned:
        logging.error("Error: news don't sent to user")
    
    
