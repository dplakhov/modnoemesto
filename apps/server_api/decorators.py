from django.http import HttpResponseNotFound
import settings

try:
    from functools import update_wrapper, wraps
except ImportError:
    from django.utils.functional import update_wrapper, wraps  # Python 2.4 fallback.

from django.utils.decorators import available_attrs

def server_only_access():
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.META.get('REMOTE_ADDR') in settings.ALLOWED_SERVER_IPS:
                return view_func(request, *args, **kwargs)
            return HttpResponseNotFound()
        return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
    return decorator


