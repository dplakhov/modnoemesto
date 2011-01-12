from django.contrib.auth.decorators import permission_required
from django.views.generic.simple import direct_to_template
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings

from models import LogEntry


def get_loggers_names():
    return LogEntry.objects.distinct('logger_name')

@permission_required('logging')
def log_list(request, page=1, level=''):
    filter_data = {}

    logger = request.GET.get('logger', None)
    if logger:
        filter_data['logger_name'] = logger

    if level:
        filter_data['levelname'] = level

    if filter_data:
        entries = LogEntry.objects.filter(**filter_data).order_by('-date')
    else:
        entries = LogEntry.objects.order_by('-date')

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
