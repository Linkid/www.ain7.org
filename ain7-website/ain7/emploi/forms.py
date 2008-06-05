# -*- coding: utf-8
#
# emploi/forms.py
#
#   Copyright (C) 2007-2008 AIn7
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

from django import newforms as forms
from django.newforms import widgets
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Track
from ain7.emploi.models import *
from ain7.fields import AutoCompleteField
from ain7.widgets import DateTimeWidget

dateWidget = DateTimeWidget()
dateWidget.dformat = '%d/%m/%Y'

class JobOfferForm(forms.Form):
    reference = forms.CharField(label=_('reference'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'50'}))
    title = forms.CharField(label=_('title').capitalize(), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'50'}))
    experience = forms.CharField(label=_('experience'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'50'}))
    contract_type = forms.IntegerField(label=_('contract type'),
        required=False)
    contract_type.widget = forms.Select(choices=JobOffer.JOB_TYPES)
    is_opened = forms.BooleanField(label=_('is opened'),required=False)
    description = forms.CharField(label=_('description').capitalize(),
        max_length=500, required=False,
        widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':95}))
    office = forms.ModelChoiceField(label=_('office').capitalize(),
        queryset=Office.objects.valid_offices(), required=True)
    contact_name = forms.CharField(label=_('Contact name'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'50'}))
    contact_email = forms.EmailField(label=_('Contact email').capitalize(),
        required=False)
    track = forms.ModelMultipleChoiceField(label=_('track').capitalize(),
        queryset=Track.objects.all(), required=False)
    

    def save(self, job_offer=None):
        if not job_offer:
            job_offer = JobOffer()
        job_offer.reference = self.cleaned_data['reference']
        job_offer.title = self.cleaned_data['title']
        job_offer.experience = self.cleaned_data['experience']
        job_offer.contract_type = self.cleaned_data['contract_type']
        job_offer.is_opened = self.cleaned_data['is_opened']
        job_offer.description = self.cleaned_data['description']
        job_offer.office = self.cleaned_data['office']
        job_offer.contact_name = self.cleaned_data['contact_name']
        job_offer.contact_email = self.cleaned_data['contact_email']
        job_offer.save()
        # needs to have a primary key before a many-to-many can be used
        job_offer.track = self.cleaned_data['track']
        job_offer.save()
        return job_offer


class SearchJobForm(forms.Form):
    title = forms.CharField(label=_('title'),max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    allTracks = forms.BooleanField(label=_('all tracks'), required=False)
    track = forms.ModelMultipleChoiceField(
        label=_('track'), queryset=Track.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(SearchJobForm, self).__init__(*args, **kwargs)

    def clean_track(self):
        return self.cleaned_data['track']

    def search(self):
        maxTrackId = Track.objects.latest('id').id + 1
        # si des filières sont sélectionnées mais pas le joker
        # on filtre par rapport à ces filières
        jobsMatchingTracks = []
        if (not self.cleaned_data['allTracks'])\
               and len(self.cleaned_data['track'])>0:
            for track in self.cleaned_data['track']:
                jobsMatchingTracks.extend(track.jobs.all())
        else:
            jobsMatchingTracks = JobOffer.objects.all()
        # maintenant on filtre ces jobs par rapport au titre saisi
        matchingJobs = []
        if self.cleaned_data['title']:
            for job in jobsMatchingTracks:
                if str(self.cleaned_data['title']) in job.title:
                    matchingJobs.append(job)
        else:
            matchingJobs = jobsMatchingTracks
        return matchingJobs

class OrganizationForm(forms.Form):
    name = forms.CharField(
        label=_('Name'), max_length=50, required=True)
    size = forms.IntegerField(
        label=_('Size'), required=True,
        widget=forms.Select(choices=Organization.ORGANIZATION_SIZE))
    activity_field = forms.CharField(
        label=_('Activity field'), max_length=50, required=True,
        widget=AutoCompleteField(url='/ajax/activityfield/'))
    short_description = forms.CharField(
        label=_('Short Description'), max_length=50)
    long_description = forms.CharField(
        label=_('Long Description'), max_length=5000, required=False,
        widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':95}))

    def save(self, is_a_proposal=False, organization=None):
        if organization:
            org = organization
        else:
            org = Organization()
        # TODO : automatiser avec qqchose comme ça:
#         for field in org._meta.fields:
#             if field.name=='is_a_proposal':
#                 field.value = is_a_proposal
#             else:
#                 field.value = self.cleaned_data[field.name]
        org.name = self.cleaned_data['name']
        org.size = self.cleaned_data['size']
        org.activity_field = ActivityField.objects.get(id=self.cleaned_data['activity_field'])
        org.short_description = self.cleaned_data['short_description']
        org.long_description = self.cleaned_data['long_description']
        org.is_a_proposal = is_a_proposal
        org.save()
        return org

class OfficeForm(forms.ModelForm):
    organization = forms.ModelChoiceField(
        label=_('organization'),
        queryset=Organization.objects.valid_organizations(),required=True)
    country = forms.ModelChoiceField(
        label=_('country'), queryset=Country.objects.all(), required=False)

    class Meta:
        model = Office
        exclude = ('is_a_proposal')

class OfficeFormNoOrg(forms.ModelForm):
    country = forms.ModelChoiceField(
        label=_('country'), queryset=Country.objects.all(), required=False)

    class Meta:
        model = Office
        exclude = ('is_a_proposal', 'organization')

class PositionForm(forms.ModelForm):
    start_date = forms.DateTimeField(label=_('start date').capitalize(),
        widget=dateWidget)
    end_date = forms.DateTimeField(label=_('end date').capitalize(),
        widget=dateWidget)
    
    class Meta:
        model = Position
        exclude = ('ain7member')

    def clean_end_date(self):
        if self.cleaned_data.get('start_date') and \
            self.cleaned_data.get('end_date') and \
            self.cleaned_data['start_date']>self.cleaned_data['end_date']:
            raise forms.ValidationError(_('Start date is later than end date'))
        return self.cleaned_data['end_date']

class EducationItemForm(forms.ModelForm):
    start_date = forms.DateTimeField(label=_('start date').capitalize(),
        widget=dateWidget)
    end_date = forms.DateTimeField(label=_('end date').capitalize(),
        widget=dateWidget)

    class Meta:
        model = EducationItem
        exclude = ('ain7member')

    def clean_end_date(self):
        if self.cleaned_data.get('start_date') and \
            self.cleaned_data.get('end_date') and \
            self.cleaned_data['start_date']>self.cleaned_data['end_date']:
            raise forms.ValidationError(_('Start date is later than end date'))
        return self.cleaned_data['end_date']

class LeisureItemForm(forms.ModelForm):
    
    class Meta:
        model = LeisureItem
        exclude = ('ain7member')

class PublicationItemForm(forms.ModelForm):
    date = forms.DateTimeField(label=_('date').capitalize(),
        widget=dateWidget)

    class Meta:
        model = PublicationItem
        exclude = ('ain7member')
