# -*- coding: utf-8 -*-
from apps.social.documents import User
try:
    from functools import update_wrapper, wraps
except ImportError:
    from django.utils.functional import update_wrapper, wraps  # Python 2.4 fallback.

from .thread_locals import _thread_locals

def with_user_theme(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user_id = kwargs.get('user_id')

        if user_id:
            user = User.objects.with_id(user_id)
        else:
            user = request.user

        if (user
            and user.is_authenticated()
            and user.profile.theme
            ):
            setattr(_thread_locals, 'current_theme', user.profile.theme)

        return view_func(request, *args, **kwargs)
    return wraps(view_func)(_wrapped_view)
