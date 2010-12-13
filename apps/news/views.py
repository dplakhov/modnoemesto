# -*- coding: utf-8 -*-
import os

from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.conf import settings

from .documents import News
from .forms import NewsForm

def news_add(request):
    raise Http404()