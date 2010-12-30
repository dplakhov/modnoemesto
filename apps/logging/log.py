import logging
import sys
from django.core import mail



class MongoHander(logging.Handler):
    def emit(self, record):
        import traceback
        from django.conf import settings

#        try:
#            if sys.version_info < (2,5):
#                # A nasty workaround required because Python 2.4's logging
#                # module doesn't support passing in extra context.
#                # For this handler, the only extra data we need is the
#                # request, and that's in the top stack frame.
#                request = record.exc_info[2].tb_frame.f_locals['request']
#            else:
#                request = record.request
#
#            subject = '%s (%s IP): %s' % (
#                record.levelname,
#                (request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS and 'internal' or 'EXTERNAL'),
#                request.path
#            )
#            request_repr = repr(request)
#        except:
#            subject = 'Error: Unknown URL'
#            request_repr = "Request repr() unavailable"
#
#        if record.exc_info:
#            stack_trace = '\n'.join(traceback.format_exception(*record.exc_info))
#        else:
#            stack_trace = 'No stack trace available'
#
#        message = "%s\n\n%s" % (stack_trace, request_repr)

        from apps.logging.models import LogEntry
        entry = LogEntry()
        entry.message = record.message
        entry.levelname = record.levelname
        entry.levelnum = record.levelno
        entry.pathname = record.pathname
        entry.logger_name = record.name
        entry.func = record.funcName
        entry.lineno = record.lineno

        entry.save()


