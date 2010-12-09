# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import permission_required
from apps.social.documents import User
from django.core.paginator import Paginator, EmptyPage, InvalidPage



@permission_required('superuser')
def statistic(request):
    return direct_to_template(request, 'admin/statistic.html', {
        'users_active_count': User.objects(is_active=True).count(),
        'users_inactive_count': User.objects(is_active=False).count(),
        'users_online_count': User.objects(last_access__gt=User.get_delta_time()).count(),
    })


@permission_required('superuser')
def user_list(request, page=1):
    #TODO: OLOLO
    on_page = 5
    page = int(page)
    q = User.objects.order_by('-date_joined')
    class ItemList(list):
        def __init__(self, *args, **kwargs):
            self.count = kwargs['count']
            del kwargs['count']
            super(ItemList, self).__init__(*args, **kwargs)
        def __getslice__(self, i, j):
            return self
        def __len__(self):
            return self.count
    count = q.count()
    items = ItemList(q[(page-1)*5:page*on_page], count=count)

    paginator = Paginator(items, on_page)
    try:
        users = paginator.page(page)
    except (EmptyPage, InvalidPage):
        users = paginator.page(paginator.num_pages)
    return direct_to_template(request, 'admin/user_list.html', {'users': users})
