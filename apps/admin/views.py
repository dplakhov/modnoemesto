# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import permission_required
from apps.social.documents import User
from apps.utils.paginator import paginate



@permission_required('statistic')
def statistic(request):
    return direct_to_template(request, 'admin/statistic.html', {
        'users_active_count': User.objects(is_active=True).count(),
        'users_inactive_count': User.objects(is_active=False).count(),
        'users_online_count': User.objects(last_access__gt=User.get_delta_time()).count(),
    })


@permission_required('statistic')
def user_list(request):
    objects = paginate(request,
                       User.objects.order_by('-date_joined'),
                       User.objects.count(),
                       25)
    return direct_to_template(request, 'admin/user_list.html', {'objects': objects})
