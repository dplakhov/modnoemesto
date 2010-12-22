from django.contrib.auth.decorators import permission_required
from django.views.generic.simple import direct_to_template
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings

from models import LogEntry


@permission_required('logging')
def log_list(request, page=1):
    entries = LogEntry.objects.all()
    try:
        paginator = Paginator(entries, settings.LOGS_PER_PAGE)
        page_entries = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page_entries = paginator.page(paginator.num_pages)

    return direct_to_template(request, 'logging/log_list.html',
                              dict(page_entries=page_entries)
                              )

@permission_required('logging')
def log_list_level(request, level=None, page=1):
    if level:
        entries = LogEntry.objects.filter(levelname=level).all()
    else:
        entries = LogEntry.objects.none()
    try:
        paginator = Paginator(entries, settings.LOGS_PER_PAGE)
        page_entries = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page_entries = paginator.page(paginator.num_pages)
    
    return direct_to_template(request, 'logging/log_list.html',
                              dict(page_entries=page_entries)
                              )
    