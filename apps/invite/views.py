# -*- coding: utf-8 -*-

from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext_lazy as _

from .forms import InviteForm
from .documents import Invite

def invite_send(request):
    form = InviteForm(request.POST or None)
    if form.is_valid():
        invite = Invite(sender=request.user,
                        recipient_email=form.cleaned_data['email'],
                        recipient_name=form.cleaned_data['name'])
        invite.save()
        invite.send()

        messages.add_message(request, messages.SUCCESS,
                             _('Invite sent'))

        return redirect('social:index')

    return direct_to_template(request, 'social/invite_send.html',
                              dict(form=form))


def invite(request, invite_id):
    if request.user.is_authenticated():
        messages.add_message(request, messages.ERROR,
                     _('The invitation is intended only for unregistered users'))

        return redirect('social:index')

    request.session['invite_id'] = invite_id

    return redirect('social:index')

  