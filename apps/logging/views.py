from django.contrib.auth.decorators import permission_required
from django.views.generic.simple import direct_to_template
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings

from apps.utils.paginator import paginate
from models import LogEntry


def get_loggers_names():
    return LogEntry.objects.distinct('logger_name')

@permission_required('logging')
def log_list(request, level=''):
    filter_data = {}

    logger = request.GET.get('logger', None)

    if logger:
        filter_data['logger_name'] = logger

    if level:
        filter_data['levelname'] = level

    if filter_data:
        query_list = LogEntry.objects.filter(**filter_data).order_by('-date')
    else:
        query_list = LogEntry.objects.order_by('-date')

    query_count = len(query_list)
    objects = paginate(request, query_list, query_count, settings.LOGS_PER_PAGE)

    loggers = get_loggers_names()

    return direct_to_template(request, 'logging/log_list.html',
                              {
                               'objects': objects,
                               'loggers': loggers,
                               'current_logger': logger,
                               'current_level': level,
                              })
