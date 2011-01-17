from django.core import mail as django_mail
from django.conf import settings
from django.utils.encoding import smart_unicode

import logging

logger = logging.getLogger('email')

MESSAGE_FORMAT = """%s:
subject - %s, 
message - %s, 
from_email - %s, 
recipient_list - %s 
"""

def send_mail(*args, **kwargs):
    if settings.DEBUG:
        str_args = tuple([smart_unicode(i) for i in args])
        logger.debug(MESSAGE_FORMAT % (('send_mail',) + str_args))
    return django_mail.send_mail(*args, **kwargs)

def send_mass_mail(*args, **kwargs):
    if settings.DEBUG:
        messages = " ".join([MESSAGE_FORMAT % (
                'send_mass_mail', subject, message, sender, recipient)
                for subject, message, sender, recipient in args[0]])
        logger.debug(messages)
    return django_mail.send_mass_mail(*args, **kwargs)
