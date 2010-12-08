from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.core.urlresolvers import reverse

from mongoengine.django.shortcuts import get_document_or_404

from .documents import Note

from .forms import NoteForm

#@login_required
def note_list(request):
    notes = Note.objects.filter(author=request.user)
    return direct_to_template(request, 'notes/note_list.html',
                              { 'notes': notes })


#@login_required
def note_edit(request, note_id=None):
    fields = ('title', 'text', 'is_public')

    if note_id:
        note = get_document_or_404(Note, id=note_id, author=request.user)

        initial = {}

        for field in fields:
            initial[field] = getattr(note, field)

    else:
        note = None
        initial = {}

    form = NoteForm(request.POST or None, initial=initial)

    if form.is_valid():
        note = note or Note(author=request.user)

        for field in fields:
            setattr(note, field, form.cleaned_data[field])

        note.save()
        return HttpResponseRedirect(reverse('notes:note_list'))

    return direct_to_template(request, 'notes/note_edit.html',
                              { 'form': form, 'create': not note })


#@login_required
def note_view(request, note_id):
    notes = Note.objects(id=note_id, author=request.user)[:] or \
        Note.objects(id=note_id, is_public=True)[:]
    if not notes:
        return HttpResponseNotFound()
    return direct_to_template(request, 'notes/note_view.html',
                              { 'note': notes[0] })


#@login_required
def note_delete(request, note_id):
    note = Note.objects(id=note_id, author=request.user) or \
        Note.objects(id=note_id, is_public=True)
    if not note:
        return HttpResponseNotFound()
    note.delete()
    return HttpResponseRedirect(reverse('notes:note_list'))
