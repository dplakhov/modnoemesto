# -*- coding: utf-8 -*-

from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext_lazy as _

from apps.utils.stringio import StringIO

from .forms import InviteForm, ImportInviteForm
from .documents import Invite

def send(request):
    send_form = InviteForm(request.POST or None)
    import_form = ImportInviteForm(request.POST or None, request.FILES)

    if send_form.is_valid():
        _send_invite(request.user,
                        send_form.cleaned_data['email'],
                        send_form.cleaned_data['name'])
        messages.add_message(request, messages.SUCCESS,
                             _('Invite sent'))


    if import_form.is_valid():
        buffer = StringIO()
        for chunk in request.FILES['file']:
            buffer.write(chunk)

        buffer.reset()

        contacts = []

        if import_form.cleaned_data['type'] == 'csv':
            import csv
            reader = csv.reader(buffer)
            for i, row in enumerate(reader):
                print i, row
                if not i:
                    pass
                else:
                    pass
        elif import_form.cleaned_data['type'] == 'vcard':
            import vobject
            vobjects = vobject.readComponents(buffer)

            while 1:
                try:
                    vcf = vcfs.next()
                    if vcf.contents.has_key('email'):
                        contacts.append((vcf.email.value,vcf.fn.value))

                except:
                    break

        else:
            raise NotImplementedError

        for (email, name) in contacts:
            _send_invite(request.user, email, name)

        messages.add_message(request, messages.SUCCESS,
                                 _('Invites sent'))

    return direct_to_template(request, 'social/invite_send.html',
                              dict(send_form=send_form,
                                   import_form=import_form
                                   ))


def _send_invite(sender, email, name):
    invite = Invite(sender=sender,
                recipient_email=email,
                recipient_name=name)
    invite.save()
    invite.send()


def invite(request, invite_id):
    if request.user.is_authenticated():
        messages.add_message(request, messages.ERROR,
                     _('The invitation is intended only for unregistered users'))

        return redirect('social:index')

    request.session['invite_id'] = invite_id

    return redirect('social:index')

  