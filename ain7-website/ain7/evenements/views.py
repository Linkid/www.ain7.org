# -*- coding: utf-8
#
# evenements/views.py
#
#   Copyright (C) 2007 AIn7
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#

import vobject

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django import newforms as forms
from django.template import RequestContext
from django.newforms import widgets
from django.http import HttpResponseRedirect, HttpResponse
from datetime import datetime

from ain7.annuaire.models import Person, UserContribution, UserContributionType
from ain7.evenements.models import Event, EventSubscription
from ain7.utils import ain7_render_to_response, ImgUploadForm
from ain7.decorators import confirmation_required

class JoinEventForm(forms.Form):
    subscriber_number = forms.IntegerField(label=_('Number of persons'))

class SubscribeEventForm(forms.Form):
    subscriber = forms.IntegerField(label=_('Person to subscribe'))
    subscriber_number = forms.IntegerField(label=_('Number of persons'))

    def __init__(self, *args, **kwargs):
        personList = []
        for person in Person.objects.all():
            personList.append( (person.user.id, str(person)) )
        self.base_fields['subscriber'].widget = \
            forms.Select(choices=personList)
        super(SubscribeEventForm, self).__init__(*args, **kwargs)

class SearchEventForm(forms.Form):
    name = forms.CharField(label=_('Event name'), max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    location = forms.CharField(label=_('Location'), max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))

def index(request):
    events = Event.objects.filter(end__gte=datetime.now())[:5]
    return ain7_render_to_response(request, 'evenements/index.html',
                            {'events': events})


def details(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return ain7_render_to_response(request, 'evenements/details.html',
                            {'event': event})

@login_required
def edit(request, event_id):

    event = get_object_or_404(Event, pk=event_id)
    image = event.image

    EventForm = forms.models.form_for_instance(event,
        formfield_callback=_form_callback)

    if request.method == 'POST':
        f = EventForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['image'] = image
            f.save()

            request.user.message_set.create(message=_('Event successfully updated.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(f.errors))

        return HttpResponseRedirect('/evenements/%s/' % (event.id))

    f = EventForm()
    next_events = Event.objects.filter(end__gte=datetime.now())

    return ain7_render_to_response(request, 'evenements/edit.html',
                                   {'form': f, 'event': event,
                                    'event_list': Event.objects.all(),
                                    'next_events': next_events})

@login_required
def image_edit(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'GET':
        form = ImgUploadForm()
        filename = None
        if event.image:
            filename = '/site_media/%s' % event.image
        return ain7_render_to_response(request, 'pages/image.html',
            {'section': 'evenements/base.html',
             'name': _("image").capitalize(), 'form': form,
             'filename': filename})
    else:
        post = request.POST.copy()
        post.update(request.FILES)
        form = ImgUploadForm(post)
        if form.is_valid():
            event.save_image_file(
                form.clean_data['img_file']['filename'],
                form.clean_data['img_file']['content'])
            request.user.message_set.create(message=_("The picture has been successfully changed."))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))
        return HttpResponseRedirect('/evenements/%s/edit/' % event.id)

@confirmation_required(lambda event_id=None, object_id=None : '', 'evenements/base.html', _('Do you really want to delete the image of this event'))
@login_required
def image_delete(request, event_id):

    event = get_object_or_404(Event, pk=event_id)
    event.image = None
    event.save()

    request.user.message_set.create(message=
        _('The image of this event has been successfully deleted.'))
    return HttpResponseRedirect('/evenements/%s/edit/' % event_id)

@login_required
def join(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        f = JoinEventForm(request.POST)
        if f.is_valid():
            subscription = EventSubscription()
            subscription.subscriber_number = request.POST['subscriber_number']
            subscription.subscriber = request.user.person
            subscription.event = event
            subscription.save()

            contrib_type = UserContributionType.objects.filter(key='event_subcription')[0]
            contrib = UserContribution(user=request.user.person, type=contrib_type)
            contrib.save()

        request.user.message_set.create(message=_('You have been successfully subscribed to this event.'))
        return HttpResponseRedirect('/evenements/%s/' % (event.id))

    # on vérifie que la personne n'est pas déjà inscrite
    person = request.user.person
    already_subscribed = False
    for subscription in person.event_subscriptions.all():
        if subscription.event == event:
            already_subscribed = True
    if already_subscribed:
        request.user.message_set.create(message=_('You have already subscribed to this event.'))
        return HttpResponseRedirect('/evenements/%s/' % event.id)

    f =  JoinEventForm()
    next_events = Event.objects.filter(end__gte=datetime.now())
    return ain7_render_to_response(request, 'evenements/join.html',
                            {'event': event, 'form': f,
                             'event_list': Event.objects.all(),
                             'next_events': next_events})

@login_required
def participants(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    return ain7_render_to_response(request, 'evenements/participants.html',
                            {'event': event})

@login_required
def register(request):

    EventForm = forms.models.form_for_model(Event,
                                            formfield_callback=_form_callback)

    if request.method == 'POST':
        f = EventForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['image'] = None
            f.save()

            contrib_type = UserContributionType.objects.filter(key='event_register')[0]
            contrib = UserContribution(user=request.user.person, type=contrib_type)
            contrib.save()

            request.user.message_set.create(message=_('Event successfully added.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(f.errors))

        #return HttpResponseRedirect('/evenements/%s/' % (f.id))
        return HttpResponseRedirect('/evenements/')

    f = EventForm()
    next_events = Event.objects.filter(end__gte=datetime.now())

    return ain7_render_to_response(request, 'evenements/register.html',
                                   {'form': f,
                                    'event_list': Event.objects.all(),
                                    'next_events': next_events})

def search(request):

    if request.method == 'POST':
        form = SearchEventForm(request.POST)
        if form.is_valid():
                    list_events = Event.objects.filter(name__icontains=form.clean_data['name'],
                                                       location__icontains=form.clean_data['location'])

        return ain7_render_to_response(request, 'evenements/search.html',
                                 {'form': form,
                                  'list_events': list_events,
                                  'request': request})

    else:
        f = SearchEventForm()
        return ain7_render_to_response(request, 'evenements/search.html', {'form': f})

@login_required
def subscribe(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        f = SubscribeEventForm(request.POST)
        person = Person.objects.filter(pk=request.POST['subscriber'])[0]
        # on vérifie que la personne n'est pas déjà inscrite
        already_subscribed = False
        for subscription in person.event_subscriptions.all():
            if subscription.event == event:
                already_subscribed = True
        if already_subscribed:
            request.user.message_set.create(message=_('This person is already subscribed to this event.'))
            return ain7_render_to_response(request, 'evenements/participants.html',
                                           {'event': event})
        if f.is_valid():
            subscription = EventSubscription()
            subscription.subscriber_number = request.POST['subscriber_number']
            subscription.subscriber = Person.objects.filter(pk=request.POST['subscriber'])[0]
            subscription.event = event
            subscription.save()

            p = subscription.subscriber

            request.user.message_set.create(message=_('You have successfully subscribed')+
                                            ' '+p.first_name+' '+p.last_name+' '+_('to this event.'))
        return HttpResponseRedirect('/evenements/%s/' % (event.id))

    f =  SubscribeEventForm()
    next_events = Event.objects.filter(end__gte=datetime.now())

    return ain7_render_to_response(request, 'evenements/subscribe.html',
                                   {'event': event, 'form': f,
                                    'event_list': Event.objects.all(),
                                    'next_events': next_events})

def ical(request):

    list_events = Event.objects.filter(end__gte=datetime.now())

    cal = vobject.iCalendar()
    cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this

    utc = vobject.icalendar.utc

    for event in list_events:
        ev = cal.add('vevent')
        ev.add('summary').value = event.name
        ev.add('location').value = event.location
        ev.add('dtstart').value = event.start
        ev.add('dtend').value = event.end
        if event.description:
            ev.add('description').value = event.description
        if event.status:
            ev.add('status').value = event.status
        if event.category:
            ev.add('category').value = event.description
        ev.add('dtstamp').value = event.modification_date

    icalstream = cal.serialize().encode('utf-8')
    response = HttpResponse(icalstream, mimetype='text/calendar')
    response['Filename'] = 'ain7.ics'  # IE needs this
    response['Content-Disposition'] = 'attachment; filename=ain7.ics'

    return response

def validate(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return ain7_render_to_response(request, 'evenements/validate.html',
                            {'event': event})

# une petite fonction pour exclure certains champs
# des formulaires crees avec form_for_model et form_for_instance
def _form_callback(f, **args):
  exclude_fields = ('image')
  if f.name in exclude_fields:
    return None
  return f.formfield(**args)

