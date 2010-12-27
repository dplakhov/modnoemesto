from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',

    (r'^', include('apps.social.urls', namespace='social')),
    (r'^cam/', include('apps.cam.urls', namespace='cam')),
    (r'^messages/', include('apps.user_messages.urls', namespace='user_messages')),
    (r'^notes/', include('apps.notes.urls', namespace='notes')),
    (r'^billing/', include('apps.billing.urls', namespace='billing')),
    url(r'^pay/pskb/$', 'apps.billing.views.operator', name='operator'),
    url(r'^pay/robokassa/', include('apps.robokassa.urls')),
    (r'^library/', include('apps.media_library.urls', namespace='media_library')),
    (r'^file/', include('apps.media.urls', namespace='media')),
    (r'^groups/', include('apps.groups.urls', namespace='groups')),
    (r'^friends/', include('apps.friends.urls', namespace='friends')),
    (r'^modmin/', include('apps.admin.urls', namespace='admin')),
    (r'^news/', include('apps.news.urls', namespace='news')),
    (r'^log/', include('apps.logging.urls', namespace='logging')),
    (r'^chat/', include('apps.chat.urls', namespace='chat')),
    
    (r'^owner/', include('apps.admin_blog.urls', namespace='admin_blog')),
    (r'^captcha/(?P<code>[\da-f]{32})/$', 'apps.supercaptcha.draw'),
    url(r'^robots.txt$', 'django.views.generic.simple.direct_to_template', name='robots_txt', kwargs={'template': 'robots.txt'}),
)

#if settings.DEBUG:
urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                            { 'document_root': settings.MEDIA_ROOT }),
        #(r'^admin-media/(?P<path>.*)$', 'django.views.static.serve',
        #                    {'document_root': settings.ADMIN_MEDIA_ROOT }),
    )
    
handler500 = 'apps.social.views.server_error'