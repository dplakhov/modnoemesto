from django.utils.translation import ugettext as _
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from mongoengine.django.shortcuts import get_document_or_404
from .documents import Group


def check_admin_right(func):
    def wrapper(request, id, *args, **kwargs):
        group = get_document_or_404(Group, id=id)
        is_admin = group.is_admin(request.user) or request.user.is_superuser
        if not is_admin:
            messages.add_message(request, messages.ERROR, _('You are not allowed.'))
            return redirect(reverse('groups:group_view', args=[id]))
        return func(request, group, *args, **kwargs)
    return wrapper