from django.contrib.auth.decorators import permission_required
from django.views.generic.simple import direct_to_template
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings

from apps.utils.paginator import paginate
from models import LogEntry


@permission_required('logging')
def log_list(request):
    filter_data = {}

    logger = request.GET.get('logger', '')

    if logger:
        filter_data['logger_name'] = logger

    message = request.GET.get('message', '')

    if message:
        filter_data['message__icontains'] = message

    level = request.GET.get('level', '')

    if level:
        filter_data['levelname'] = level.upper()

    if filter_data:
        query_list = LogEntry.objects.filter(**filter_data).order_by('-date')
    else:
        query_list = LogEntry.objects.order_by('-date')

    query_count = len(query_list)
    objects = paginate(request, query_list, query_count, settings.LOGS_PER_PAGE)

    return direct_to_template(request, 'logging/log_list.html',
                              {
                               'objects': objects,
                               'loggers': LogEntry.objects.distinct('logger_name'),
                               'current_logger': logger,
                               'levels': ['info', 'debug', 'warning', 'error', 'critical'],
                               'current_level': level,
                              })
