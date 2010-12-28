# -*- coding: utf-8 -*-

from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound

def notify_online(request):
    pass

def notify_offline(request):
    pass

def notify_reset(request):
    pass
