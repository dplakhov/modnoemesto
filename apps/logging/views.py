from django.contrib.auth.decorators import permission_required
from django.views.generic.simple import direct_to_template
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings

from models import LogEntry


def get_loggers_names():
    return LogEntry.objects.distinct('logger_name')

@permission_required('logging')
def log_list(request, page=1):
    entries = LogEntry.objects.order_by('-date')

    logger = request.GET.get('logger', None)
    if logger:
        entries = entries.filter(logger_name=logger)

    try:
        paginator = Paginator(entries, settings.LOGS_PER_PAGE)
        page_entries = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page_entries = paginator.page(paginator.num_pages)

    loggers = get_loggers_names()

    return direct_to_template(request, 'logging/log_list.html',
                              {
                               'page_entries': page_entries,
                               'loggers': loggers,
                               'current_logger': logger,
                               'current_level': '',
                              })

@permission_required('logging')
def log_list_level(request, level=None, page=1):
    if level:
        entries = LogEntry.objects.filter(levelname=level).order_by('-date')
    else:
        entries = LogEntry.objects.none()

    logger = request.GET.get('logger', None)
    if logger:
        entries = entries.filter(logger_name=logger)

    try:
        paginator = Paginator(entries, settings.LOGS_PER_PAGE)
        page_entries = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page_entries = paginator.page(paginator.num_pages)

    loggers = get_loggers_names()

    return direct_to_template(request, 'logging/log_list.html',
                              {
                               'page_entries': page_entries,
                               'loggers': loggers,
                               'current_logger': logger,
                               'current_level': level,
                              })
