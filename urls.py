import os
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^loginza/', include('loginza.urls')),

    (r'^', include('apps.social.urls', namespace='social')),
    (r'^cam/', include('apps.cam.urls', namespace='cam')),
    (r'^messages/', include('apps.user_messages.urls', 
     namespace='user_messages')),
    (r'^notes/', include('apps.notes.urls', namespace='notes')),
    (r'^billing/', include('apps.billing.urls', namespace='billing')),
    url(r'^pay/pskb/$', 'apps.billing.views.operator', name='operator'),
    url(r'^pay/robokassa/', include('apps.robokassa.urls')),
    (r'^library/', include('apps.media_library.urls', 
     namespace='media_library')),
    (r'^file/', include('apps.media.urls', namespace='media')),
    (r'^groups/', include('apps.groups.urls', namespace='groups')),
    (r'^friends/', include('apps.friends.urls', namespace='friends')),
    (r'^modmin/', include('apps.admin.urls', namespace='admin')),
    (r'^news/', include('apps.news.urls', namespace='news')),
    (r'^log/', include('apps.logging.urls', namespace='logging')),
    (r'^chat/', include('apps.chat.urls', namespace='chat')),
    (r'^srv/', include('apps.server_api.urls', namespace='server_api')),
    (r'^api/', include('apps.server_api.urls', namespace='server_api')),
    (r'^invite/', include('apps.invite.urls', namespace='invite')),
    (r'^theme/', include('apps.themes.urls', namespace='themes')),
    (r'^owner/', include('apps.admin_blog.urls', namespace='admin_blog')),
    (r'^captcha/(?P<code>[\da-f]{32})/$', 'apps.supercaptcha.draw'),
    (r'^video_call/', include('apps.video_call.urls', namespace='video_call')),
    url(r'^robots.txt$', 'django.views.generic.simple.direct_to_template', 
        name='robots_txt', kwargs={'template': 'robots.txt'}),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', 
     {'packages': 'django.conf'}),

)

#if settings.DEBUG:
urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                            { 'document_root': settings.MEDIA_ROOT }),
        #(r'^admin-media/(?P<path>.*)$', 'django.views.static.serve',
        #                    {'document_root': settings.ADMIN_MEDIA_ROOT }),
    )

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^themes/(?P<path>.*)$', 'django.views.static.serve',
                            { 'document_root':
                              os.path.join(
                                  settings.MEDIA_ROOT,
                                  os.path.pardir,
                                  'themes'
                              ),
                              'show_indexes': True
                              }),
    )


if settings.SITE_DOMAIN == 'mestovstrechi.piter.tv':
    urlpatterns.insert(0,
       url(r'^conference/', include('apps.groups.urls', namespace='groups')))



handler500 = 'apps.social.views.server_error'
