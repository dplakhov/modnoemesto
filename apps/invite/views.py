# -*- coding: utf-8 -*-

import csv
import codecs
from apps.social.documents import User

import vobject
import chardet

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
            encoding = chardet.detect(buffer.read())['encoding']
            buffer.reset()
            reader = codecs.getreader(encoding)(buffer)
            buffer = StringIO()
            buffer.write('\n'.join(reader.readlines()).encode('utf-8'))
            buffer.reset()

            reader = csv.DictReader(buffer)
            for row in reader:
                email = row['E-mail Address']
                first_name = row['First Name']
                last_name = row['Last Name']
                contacts.append((email, ('%s %s' %
                                        (first_name, last_name)).decode('utf-8')))

        elif import_form.cleaned_data['type'] == 'vcard':
            vobjects = vobject.readComponents(buffer)

            while 1:
                try:
                    vcf = vcfs.next()
                    if vcf.contents.has_key('email'):
                        contacts.append((vcf.email.value,
                                         vcf.fn.value))

                except:
                    break

        else:
            raise NotImplementedError

        sent_count = 0
        for (email, name) in contacts:
            if _send_invite(request.user, email, name):
                sent_count += 1

        messages.add_message(request, messages.SUCCESS,
                                 _('%(sent_count)d invites sent') %
                                 dict(sent_count=sent_count))

    return direct_to_template(request, "invite/send.html",
                              dict(send_form=send_form,
                                   import_form=import_form
                                   ))


def _send_invite(sender, email, name):
    if User.objects(email=email).count():
        return False

    invite = Invite(sender=sender,
                recipient_email=email,
                recipient_name=name)

    invite.save()
    invite.send()

    return True



def invite(request, invite_id):
    if request.user.is_authenticated():
        messages.add_message(request, messages.ERROR,
                     _('The invitation is intended only for unregistered users'))

        return redirect('social:index')

    request.session['invite_id'] = invite_id

    return redirect('social:index')

  