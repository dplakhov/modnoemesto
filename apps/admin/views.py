# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import permission_required
from apps.social.documents import User
from django.core.paginator import EmptyPage, InvalidPage
from apps.utils.paginator import Paginator



@permission_required('statistic')
def statistic(request):
    return direct_to_template(request, 'admin/statistic.html', {
        'users_active_count': User.objects(is_active=True).count(),
        'users_inactive_count': User.objects(is_active=False).count(),
        'users_online_count': User.objects(last_access__gt=User.get_delta_time()).count(),
    })


@permission_required('statistic')
def user_list(request, page=1):
    paginator = Paginator(User.objects.order_by('-date_joined'), 25, User.objects.count())
    try:
        users = paginator.page(page)
    except (EmptyPage, InvalidPage):
        users = paginator.page(paginator.num_pages)
    return direct_to_template(request, 'admin/user_list.html', {'users': users})
