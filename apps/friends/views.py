# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template

def friend_list(request):
    return direct_to_template(request, 'social/profile/user_friends.html',
            dict(frends=request.user.friends))
