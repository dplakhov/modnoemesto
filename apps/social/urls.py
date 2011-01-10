# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from django.conf import settings

urlpatterns = patterns('apps.social.views',
   url(r'^$', 'index', name='index'),
   url(r'^filter/$', 'filter', name='filter'),
   url(r'^static/(?P<page>[a-z]+)/$', 'static', name='static'),
   url(r'^in_dev/$', 'in_dev', name='in_dev'),
   url(r'^home/$', 'home', name='home'),
   url(r'^home/edit/$', 'profile_edit', name='profile_edit'),

   url(r'^logout/$', 'logout', name='logout'),
   url(r'^login/$', 'index', name='login'),

   url(r'^activation/(?P<code>[a-f0-9]{12})/$', 'activation', name='activation'),
   url(r'^lostpassword/$', 'lost_password', name='lost_password'),
   url(r'^resendactivationcode/$', 'lost_password', name='resend_activation_code', kwargs={'template': 'social/resend_activation_code.html'}),
   url(r'^recoverypassword/(?P<code>[a-f0-9]{12})/$', 'recovery_password', name='recovery_password'),
   url(r'^changepassword/(?P<code>[a-f0-9]{12})/$', 'set_new_password', name='set_new_password'),

   url(r'^users/(?P<user_id>[a-f0-9]{24})/$', 'user', name='user'),

   url(r'^profile/$', 'profile_edit', name='profile_edit'),
   url(r'^profile/avatar/$', 'avatar_edit', name='avatar_edit'),

   url(r'^invite/send/$', 'invite_send', name='invite_send'),

   url(r'^invite/(?P<invite_id>[a-f0-9]{24})/$', 'invite', name='invite'),

   
   # тестовые страницы
   url(ur'^ЕГГОГ$', 'test_error',),
   url(ur'^СООБЩ$', 'test_messages',),
)
