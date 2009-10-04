# -*- coding: utf-8
#
# manage/views.py
#
#   Copyright © 2007-2009 AIn7
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

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator, InvalidPage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7.utils import ain7_render_to_response, ain7_generic_edit, ain7_generic_delete, check_access
from ain7.decorators import confirmation_required
from ain7.emploi.models import Organization, Office, ActivityField
from ain7.emploi.models import OrganizationProposal, OfficeProposal, JobOffer
from ain7.emploi.forms import OrganizationForm, OfficeForm, OfficeFormNoOrg
from ain7.manage.models import *
from ain7.manage.forms import *
from ain7.annuaire.forms import PersonForm
from ain7.annuaire.models import Person
from ain7.search_engine.models import *
from ain7.search_engine.utils import *
from ain7.search_engine.views import *


def organization_search_engine():
    return get_object_or_404(SearchEngine, name="organization")

@login_required
def index(request):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    return ain7_render_to_response(request, 'manage/default.html',
        {'notifications': Notification.objects.all()})

@login_required
def users_search(request):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    form = SearchUserForm()
    nb_results_by_page = 25
    persons = False
    paginator = Paginator(Group.objects.none(),nb_results_by_page)
    page = 1

    if request.GET.has_key('last_name') or request.GET.has_key('first_name') or \
       request.GET.has_key('organization'):
        form = SearchUserForm(request.GET)
        if form.is_valid():
            persons = form.search()
            paginator = Paginator(persons, nb_results_by_page)
            try:
                page = int(request.GET.get('page', '1'))
                persons = paginator.page(page).object_list
            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'manage/users_search.html',
        {'form': form, 'persons': persons, 'request': request,
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.num_pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count})

@login_required
def user_details(request, user_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    u = get_object_or_404(User, pk=user_id)
    return ain7_render_to_response(
        request, 'manage/user_details.html', {'this_user': u})

@login_required
def user_register(request):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

    form = NewPersonForm()

    if request.method == 'POST':
        form = NewPersonForm(request.POST)
        if form.is_valid():
            new_person = form.save()
            request.user.message_set.create(
                message=_("New user successfully created"))
            return HttpResponseRedirect(
                '/manage/users/%s/' % (new_person.user.id))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'manage/edit_form.html',
        {'action_title': _('Register new user'), 'back': back, 'form': form})

@login_required 
def user_edit(request, user_id=None): 

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r
 
    p = get_object_or_404(Person, pk=user_id) 
    return ain7_render_to_response(request, 'manage/user_edit.html', {'person': p}) 

@login_required
def user_person_edit(request, user_id=None):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r
 
    person = None
    if user_id:
        person = Person.objects.get(user=user_id)
    return ain7_generic_edit(
        request, person, PersonForm, {'user': person.user},
        'manage/edit_form.html',
        {'action_title': _("Modification of personal data for"),
         'person': person, 'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/manage/users/%s/edit/' % (person.user.id),
        _("Modifications have been successfully saved."))

@login_required
def organizations_search(request):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r
 
    form = SearchOrganizationForm()
    nb_results_by_page = 25
    organizations = False
    paginator = Paginator(Organization.objects.none(),nb_results_by_page)
    page = 1
    if request.GET.has_key('name') or request.GET.has_key('activity_field') or \
       request.GET.has_key('activity_code'):
        form = SearchOrganizationForm(request.GET)
        if form.is_valid():
            criteria = form.criteria()
            organizations = form.search(criteria)
            request.session['filter'] = criteria
            paginator = Paginator(organizations, nb_results_by_page)
            try:
                page = int(request.GET.get('page', '1'))
                organizations = paginator.page(page).object_list
            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'manage/organizations_search.html',
        {'form': form, 'organizations': organizations,
         'nb_org': Organization.objects.valid_organizations().count(),
         'nb_offices': Office.objects.valid_offices().count(),
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page, 'pages': paginator.num_pages,
         'next_page': page + 1, 'previous_page': page - 1,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count})

@login_required
def organizations_adv_search(request):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    filtr = organization_search_engine()\
            .unregistered_filters(request.user.person)
    if filtr:
        return ain7_render_to_response(request,
            'manage/organizations_adv_search.html',
            dict_for_filter(request, filtr.id))
    else:
        return ain7_render_to_response(request,
            'manage/organizations_adv_search.html',
            dict_for_filter(request, None))

@login_required
def filter_details(request, filter_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    return ain7_render_to_response(request,
        'manage/organizations_adv_search.html',
        dict_for_filter(request, filter_id))


@login_required
def dict_for_filter(request, filter_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    offices = False
    p = request.user.person
    nb_results_by_page = 25
    paginator = Paginator(Office.objects.none(),nb_results_by_page)
    page = 1
    sf = None
    if filter_id:
        sf = get_object_or_404(SearchFilter, pk=filter_id)
        
    if request.method == 'POST':

        offices = Office.objects.all()
        if filter_id:
            offices = sf.search()
        paginator = Paginator(offices, nb_results_by_page)

        try:
            page = int(request.GET.get('page', '1'))
            offices = paginator.page(page).object_list
        except InvalidPage:
            raise http.Http404

    return {'offices': offices,
         'filtr': sf,
         'nb_org': Organization.objects.valid_organizations().count(),
         'nb_offices': Office.objects.valid_offices().count(),
         'userFilters': organization_search_engine().registered_filters(p),
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.num_pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count}

@login_required
def filter_details(request, filter_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    return ain7_render_to_response(request,
        'manage/organizations_adv_search.html',
        dict_for_filter(request, filter_id))

@login_required
def filter_swapOp(request, filter_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    return se_filter_swapOp(request, filter_id,
                            reverse(filter_details, args =[ filter_id ]),
                            reverse(organizations_adv_search))

@login_required
def filter_register(request):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    sf = organization_search_engine().\
         unregistered_filters(request.user.person)
    if not sf:
        return HttpResponseRedirect(reverse(organizations_adv_search))

    form = SearchFilterForm()

    if request.method != 'POST':
        return ain7_render_to_response(request,
            'manage/edit_form.html',
            {'form': form, 'back': request.META.get('HTTP_REFERER', '/'),
             'action_title': _("Enter parameters of your filter")})
    else:
        form = SearchFilterForm(request.POST)
        if form.is_valid():
            fName = form.cleaned_data['name']
            # First we check that the user does not have
            # a filter with the same name
            sameName = organization_search_engine().\
                registered_filters(request.user.person).\
                filter(name=fName).count()
            if sameName>0:
                request.user.message_set.create(message=_("One of your filters already has this name."))
                return HttpResponseRedirect(reverse(organizations_adv_search))

            # Set the registered flag to True
            sf.registered = True
            sf.name = fName
            sf.save()

            # Redirect to filter page
            request.user.message_set.create(
                message=_("Modifications have been successfully saved."))
            return HttpResponseRedirect(
                reverse(filter_details, args=[ sf.id ]))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))
        return HttpResponseRedirect(reverse(organizations_adv_search))


@login_required
def filter_edit(request, filter_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    form = SearchFilterForm(instance=filtr)

    if request.method == 'POST':
        form = SearchFilterForm(request.POST, instance=filtr)
        if form.is_valid():
            form.cleaned_data['user'] = filtr.user
            form.cleaned_data['operator'] = filtr.operator
            form.save()
            request.user.message_set.create(message=_("Modifications have been successfully saved."))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))
        return HttpResponseRedirect(
            reverse(filter_details, args=[ filter_id ]))
    return ain7_render_to_response(
        request, 'manage/edit_form.html',
        {'form': form, 'action_title': _("Modification of the filter")})


@login_required
def remove_criteria(request, filtr):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    for crit in filtr.criteriaField.all():  crit.delete()
    for crit in filtr.criteriaFilter.all(): crit.delete()
    # TODO non recursivite + supprimer filtres sans criteres
    return

@login_required
def filter_reset(request, filter_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    remove_criteria(request, filtr)
    if filtr.registered:
        return HttpResponseRedirect(
            reverse(filter_details, args=[ filter_id ]))
    else:
        return HttpResponseRedirect(reverse(organizations_adv_search))

@login_required
def filter_delete(request, filter_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    try:
        # remove criteria linked to this filter from database
        remove_criteria(request, filtr)
        # now remove the filter
        filtr.delete()
        request.user.message_set.create(
            message=_("Your filter has been successfully deleted."))
    except KeyError:
        request.user.message_set.create(
            message=_("Something went wrong. The filter has not been deleted."))    
    return HttpResponseRedirect(reverse(organizations_adv_search))

@login_required
def filter_new(request):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    filtr = organization_search_engine().unregistered_filters(request.user.person)
    if not filtr:
        return HttpResponseRedirect(reverse(organizations_adv_search))
    remove_criteria(request, filtr)
    if filtr.registered:
        return HttpResponseRedirect(
            reverse(filter_details, args=[ filter_id ]))
    else:
        return HttpResponseRedirect(reverse(organizations_adv_search))

@login_required
def criterion_add(request, filter_id=None, criterionType=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    redirect = reverse(organizations_adv_search)
    if filter_id: redirect = reverse(filter_details, args=[ filter_id ])
    return se_criterion_add(request, organization_search_engine(),
        filter_id, criterionType, criterionField_edit,
        redirect, 'manage/org_criterion_add.html')

@login_required
def criterionField_edit(request, filter_id=None, criterion_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    return se_criterionField_edit(request, organization_search_engine(),
        filter_id, criterion_id, reverse(filter_details, args=[filter_id]),
        reverse(organizations_adv_search),
        'manage/org_criterion_edit.html')

@login_required
def criterionFilter_edit(request, filter_id=None, criterion_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    return se_criterionFilter_edit(request, organization_search_engine(),
        filter_id, criterion_id, reverse(filter_details, args=[filter_id]),
        'manage/org_criterionFilter_edit.html')

@login_required
def criterion_delete(request, filtr_id=None, crit_id=None, crit_type=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    return se_criterion_delete(request, filtr_id, crit_id, crit_type,
        reverse(filter_details, args=[filtr_id]),
        reverse(organizations_adv_search))

@login_required
def organization_edit(request, organization_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    organization = None
    if organization_id:
        organization = get_object_or_404(Organization, pk=organization_id)
        form = OrganizationForm(
            {'name': organization.name, 'size': organization.size,
             'employment_agency': organization.employment_agency,
             'activity_field': organization.activity_field.pk,
             'short_description': organization.short_description,
             'long_description': organization.long_description })
        action_title = _('Edit an organization')
    else:
        form = OrganizationForm()
        action_title = _('Register an organization')

    if request.method == 'POST':
        form = OrganizationForm(request.POST.copy())
        if form.is_valid():
            org = form.save(request.user, is_a_proposal=False, organization=organization)
            if organization:
                msg = _('Organization successfully modified')
            else:
                msg = _('Organization successfully validated')
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect('/manage/organizations/%s/' % org.id)
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No organization registered.'))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request,
        'manage/organization_edit.html',
        {'action_title': action_title, 'form': form, 'back': back})


@login_required
def organization_details(request, organization_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    c = get_object_or_404(Organization, pk=organization_id)
    return ain7_render_to_response(request, 'manage/organization_details.html',
                                   {'organization': c})

@login_required
def export_csv(request):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    if not request.session.has_key('filter'):
        request.user.message_set.create(message=_("You have to make a search before using csv export."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    criteria = request.session['filter']
    orgs = Organization.objects.filter(**criteria).distinct()
    offices = Office.objects.filter(organization__in=orgs)

    return se_export_csv(request, offices, organization_search_engine(),
        'manage/edit_form.html')

@login_required
def adv_export_csv(request, filter_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    se = organization_search_engine()
    if not filter_id and not se.unregistered_filters(request.user.person):
        request.user.message_set.create(message=
            _("You have to make a search before using csv export."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    if filter_id:
        sf = get_object_or_404(SearchFilter, id=filter_id)
    else:
        sf = se.unregistered_filters(request.user.person)
    return se_export_csv(request, sf.search(), se, 'manage/edit_form.html')

@confirmation_required(
    lambda user_id=None,
    organization_id=None: str(get_object_or_404(Organization, pk=organization_id)),
    'manage/base.html',
    _('Do you REALLY want to delete this organization'))
def organization_delete(request, organization_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    organization = get_object_or_404(Organization, pk=organization_id)
    organization.delete()
    request.user.message_set.create(
        message=_('Organization successfully removed'))
    return HttpResponseRedirect('/manage/')


@login_required
def organization_merge(request, organization_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    organization = get_object_or_404(Organization, pk=organization_id)

    # 1er passage : on demande la saisie d'une deuxième organisation
    if request.method == 'GET':
        f = OrganizationListForm()
        return ain7_render_to_response(
            request, 'manage/organization_merge.html',
            {'form': f, 'organization': organization})

    # 2e passage : sauvegarde, notification et redirection
    if request.method == 'POST':
        f = OrganizationListForm(request.POST.copy())
        if f.is_valid():
            organization2 = f.search()
            if organization2:
                if organization2 != organization:
                    return HttpResponseRedirect('/manage/organizations/%s/merge/%s/' % (organization2.id, organization_id))
                else:
                    request.user.message_set.create(message=_('The two organizations are the same. No merging.'))
        request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
        return HttpResponseRedirect('/manage/organizations/%s/merge/' %
            organization_id)
        

@confirmation_required(
    lambda user_id=None, org1_id=None, org2_id=None:
    str(get_object_or_404(Organization, pk=org2_id)) + _(' replaced by ') + \
    str(get_object_or_404(Organization, pk=org1_id)),
    'manage/base.html',
    _('Do you REALLY want to have'))
def organization_do_merge(request, org1_id, org2_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    org1 = get_object_or_404(Organization, pk=org1_id)
    org2 = get_object_or_404(Organization, pk=org2_id)
    org1.merge(org2)
    request.user.message_set.create(
        message=_('Organizations successfully merged'))
    return HttpResponseRedirect('/manage/organizations/%s/' % org1_id)

@login_required
def organization_register_proposal(request, proposal_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    if not proposal_id:
        return HttpResponseRedirect('/manage/')
    
    proposal = get_object_or_404(OrganizationProposal, pk=proposal_id)
    form = OrganizationForm(
        {'name': proposal.modified.name,
         'size': proposal.modified.size,
         'employment_agency': proposal.modified.employment_agency,
         'activity_field': proposal.modified.activity_field.pk,
         'short_description': proposal.modified.short_description, 
         'long_description': proposal.modified.long_description })

    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            org = proposal.modified
            org.name = form.cleaned_data['name']
            org.employment_agency = form.cleaned_data['employment_agency']
            org.size = form.cleaned_data['size']
            org.activity_field = ActivityField.objects.get(
                pk=form.cleaned_data['activity_field'])
            org.short_description = form.cleaned_data['short_description']
            org.long_description = form.cleaned_data['long_description']
            org.is_a_proposal = False
            org.is_valid = True
            org.logged_save(request.user.person)
            # on supprime la notification et la proposition
            notification = Notification.objects.get(
                organization_proposal=proposal )
            if notification:
                notification.delete()
            proposal.delete()
            request.user.message_set.create(message=_('Organization successfully validated'))
            return HttpResponseRedirect('/manage/')
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No organization registered.') + str(form.errors))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request,
        'manage/proposal_register.html',
        {'action_title': _('Validate a new organization'),
         'form': form, 'back': back})

@login_required
def organization_edit_proposal(request, proposal_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    if not proposal_id:
        return HttpResponseRedirect('/manage/')
    
    proposal = get_object_or_404(OrganizationProposal, pk=proposal_id)
    form = OrganizationForm(
        {'name': proposal.modified.name,
         'size': proposal.modified.size,
         'employment_agency': proposal.modified.employment_agency,
         'activity_field': proposal.modified.activity_field.pk,
         'short_description': proposal.modified.short_description, 
         'long_description': proposal.modified.long_description })

    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save(user=request.user,
                                     is_a_proposal=False,
                                     organization=proposal.original)
            # on supprime la notification et la proposition
            notification = Notification.objects.get(
                organization_proposal=proposal )
            notification.delete()
            proposal.modified.really_delete()
            proposal.delete()
            request.user.message_set.create(message=_('Organization successfully modified'))
            return HttpResponseRedirect('/manage/')
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            
    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request,
        'manage/proposal_edit_organization.html',
        {'form': form, 'original': proposal.original, 'back': back})

@login_required
def organization_delete_proposal(request, proposal_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    proposal = get_object_or_404(OrganizationProposal, pk=proposal_id)
    org = proposal.original
    back = request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        org.delete()
        notification = Notification.objects.get(organization_proposal=proposal)
        notification.delete()
        request.user.message_set.create(
            message=_('Organization successfully removed'))
        return HttpResponseRedirect('/manage/')
    return ain7_render_to_response(request, 'manage/organization_details.html',
        {'organization': org, 'back': back, 'action': 'propose_deletion'})

@login_required
def office_edit(request, office_id=None, organization_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    office = None
    if office_id:
        return ain7_generic_edit(
            request, get_object_or_404(Office, pk=office_id),
            OfficeForm, {'is_a_proposal': False, 'is_valid': True},
            'manage/organization_edit.html',
            {'action_title': _('Edit an office'),
             'back': request.META.get('HTTP_REFERER', '/')}, {},
            '/manage/offices/%s/' % office_id,
            _('Office successfully modified'))
    else:
        return ain7_generic_edit(
            request, None, OfficeForm,
            {'is_a_proposal': False, 'is_valid': True},
            'manage/organization_edit.html',
            {'action_title': _('Register an office'),
             'back': request.META.get('HTTP_REFERER', '/')}, {},
            '/manage/offices/$objid/', _('Office successfully created'))

@login_required
def office_details(request, office_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    office = get_object_or_404(Office, pk=office_id)
    return ain7_render_to_response(request, 'manage/office_details.html',
        {'office': office})


@confirmation_required(
    lambda user_id=None,
    office_id=None: str(get_object_or_404(Office, pk=office_id)),
    'manage/base.html', _('Do you REALLY want to delete this office'))
@login_required
def office_delete(request, office_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    office = get_object_or_404(Office, pk=office_id)
    organization_id = office.organization.id
    return ain7_generic_delete(request,
        get_object_or_404(Office, pk=office_id),
        '/manage/organizations/%s/' % organization_id,
        _('Office successfully removed'))


@login_required
def office_merge(request, office_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    office = get_object_or_404(Office, pk=office_id)

    # 1er passage : on demande la saisie d'une deuxième organisation
    if request.method == 'GET':
        f = OfficeListForm()
        return ain7_render_to_response(
            request, 'manage/office_merge.html', {'form':f, 'office':office})

    # 2e passage : sauvegarde, notification et redirection
    if request.method == 'POST':
        f = OfficeListForm(request.POST.copy())
        if f.is_valid():
            office2 = f.search()
            if office2:
                if office2 != office:
                    return HttpResponseRedirect('/manage/offices/%s/merge/%s/' % (office2.id, office_id))
                else:
                    request.user.message_set.create(message=_('The two offices are the same. No merging.'))
        request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(f.errors))
        return HttpResponseRedirect('/manage/offices/%s/merge/' % office_id)
        

@confirmation_required(
    lambda user_id=None, office1_id=None, office2_id=None:
    unicode(get_object_or_404(Office, pk=office2_id)) + _(' replaced by ') + \
    unicode(get_object_or_404(Office, pk=office1_id)),
    'manage/base.html',
    _('Do you REALLY want to have'))
def office_do_merge(request, office1_id, office2_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    office1 = get_object_or_404(Office, pk=office1_id)
    office2 = get_object_or_404(Office, pk=office2_id)
    office1.merge(office2)
    request.user.message_set.create(message=_('Offices successfully merged'))
    return HttpResponseRedirect('/manage/offices/%s/' % office1_id)


@login_required
def office_register_proposal(request, proposal_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    if not proposal_id:
        return HttpResponseRedirect('/manage/')
    
    proposal = get_object_or_404(OfficeProposal, pk=proposal_id)
    form = OfficeForm(instance=proposal.modified)

    if request.method == 'POST':
        form = OfficeForm(request.POST.copy(), instance=proposal.modified)
        if form.is_valid():
            office = proposal.modified
            office.organization = form.cleaned_data['organization']
            office.name = form.cleaned_data['name']
            office.line1 = form.cleaned_data['line1']
            office.line2 = form.cleaned_data['line2']
            office.zip_code = form.cleaned_data['zip_code']
            office.city = form.cleaned_data['city']
            office.country = form.cleaned_data['country']
            office.phone_number = form.cleaned_data['phone_number']
            office.web_site = form.cleaned_data['web_site']
            office.is_a_proposal = False
            office.is_valid = True
            office = form.save()
            # on supprime la notification et la proposition
            notification = Notification.objects.get(office_proposal=proposal)
            if notification:
                notification.delete()
            proposal.delete()
            request.user.message_set.create(message=_('Office successfully validated'))
            return HttpResponseRedirect('/manage/')
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.') + str(form.errors))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request,
        'manage/proposal_register.html',
        {'action_title': _('Validate a new office'),
         'form': form, 'back': back})

@login_required
def office_edit_proposal(request, proposal_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    if not proposal_id:
        return HttpResponseRedirect('/manage/')
    
    proposal = get_object_or_404(OfficeProposal, pk=proposal_id)
    initDict = {'name': proposal.modified.name,
                'line1': proposal.modified.line1,
                'line2': proposal.modified.line2,
                'zip_code': proposal.modified.zip_code,
                'city': proposal.modified.city,
                'country': proposal.modified.country,
                'phone_number': proposal.modified.phone_number,
                'web_site': proposal.modified.web_site }
    form = OfficeFormNoOrg(initDict)

    if request.method == 'POST':
        form = OfficeFormNoOrg(request.POST)
        if form.is_valid():
            proposal.original.name = form.cleaned_data['name']
            proposal.original.line1 = form.cleaned_data['line1']
            proposal.original.line2 = form.cleaned_data['line2']
            proposal.original.zip_code = form.cleaned_data['zip_code']
            proposal.original.city = form.cleaned_data['city']
            proposal.original.country = form.cleaned_data['country']
            proposal.original.phone_number = form.cleaned_data['phone_number']
            proposal.original.web_site = form.cleaned_data['web_site']
            proposal.original.save()
            # on supprime la notification et la proposition
            notification = Notification.objects.get( office_proposal=proposal )
            notification.delete()
            proposal.modified.really_delete()
            proposal.delete()
            request.user.message_set.create(message=_('Office successfully modified'))
            return HttpResponseRedirect('/manage/')
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            
    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request,
        'manage/proposal_edit_office.html',
        {'form': form, 'original': proposal.original, 'back': back})

@login_required
def office_delete_proposal(request, proposal_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    proposal = get_object_or_404(OfficeProposal, pk=proposal_id)
    office = proposal.original
    back = request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        return HttpResponseRedirect('/manage/offices/%d/delete/'% office.id)
    return ain7_render_to_response(request, 'manage/office_details.html',
        {'office': office, 'back': back, 'action': 'propose_deletion'})

@login_required
def roles_index(request):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

    roles = Group.objects.all()

    return ain7_render_to_response(request, 'manage/role_index.html',
        {'roles': roles, 'request': request})

@login_required
def role_register(request):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

    form = NewRoleForm()

    if request.method == 'POST':
        form = NewRoleForm(request.POST)
        if form.is_valid():

            if not Group.objects.filter(name=form.cleaned_data['name']).count() == 0:
                request.user.message_set.create(message=_("Several roles have the same name. Please choose another one"))

            else:
                new_role = form.save()
                request.user.message_set.create(
                    message=_("New role successfully created"))
                return HttpResponseRedirect(
                    '/manage/roles/%s/' % (new_role.name))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'manage/edit_form.html',
        {'action_title': _('Register new role'), 'back': back, 'form': form})


@login_required
def role_details(request, role_id):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

    g = get_object_or_404(Group, name=role_id)
    return ain7_render_to_response(request, 'manage/role_details.html', {'role': g})

@login_required
def role_member_add(request, role_id):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

    g = get_object_or_404(Group, name=role_id)

    form = MemberRoleForm()

    if request.method == 'POST':
        form = MemberRoleForm(request.POST)
        if form.is_valid():
            u = User.objects.get(id=form.cleaned_data['username'])
            u.groups.add(g)
            request.user.message_set.create(message=_('User added to role'))
            return HttpResponseRedirect('/manage/roles/%s/' % role_id)
        else:
            request.user.message_set.create(message=_('User is not correct'))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request, 'manage/role_user_add.html',
                            {'form': form, 'role': g, 'back': back})

@login_required
def role_member_delete(request, role_id, member_id):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

    group = get_object_or_404(Group, name=role_id)
    member = get_object_or_404(User, pk=member_id)

    member.groups.remove(group)

    request.user.message_set.create(message=_('Member removed from role'))

    return HttpResponseRedirect('/manage/roles/%s/' % role_id)

@login_required
def notification_add(request):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    return ain7_generic_edit(
        request, None, NotificationForm,
        {'organization_proposal': None, 'office_proposal': None,
         'job_proposal': None},
        'manage/notification.html',
        {'action_title': _('Add a new notification'),
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/manage/', _('Notification successfully created'))

@login_required
def notification_edit(request, notif_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    return ain7_generic_edit(
        request, get_object_or_404(Notification, pk=notif_id),
        NotificationForm,
        {'organization_proposal': None, 'office_proposal': None,
         'job_proposal': None},
        'manage/notification.html',
        {'action_title': _("Modification of the notification"),
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/manage/', _("Modifications have been successfully saved."))

@confirmation_required(
    lambda user_id=None,
    notif_id=None: str(get_object_or_404(Notification, pk=notif_id)),
    'manage/base.html',
    _('Do you REALLY want to delete the notification'))
def notification_delete(request, notif_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    notif = get_object_or_404(Notification, pk=notif_id)
    notif.delete()
    request.user.message_set.create(
        message=_("The notification has been successfully removed."))
    return HttpResponseRedirect('/manage/')

# Adresses
@login_required
def user_address_edit(request, user_id=None, address_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    person = get_object_or_404(Person, user=user_id)
    address = None
    title = _('Creation of an address for')
    msgDone = _('Address successfully added.')
    if address_id:
        address = get_object_or_404(Address, pk=address_id)
        title = _('Modification of an address for')
        msgDone = _('Address informations updated successfully.')
    return ain7_generic_edit(
        request, address, AddressForm, {'person': person},
        'manage/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/manage/users/%s/edit/#address' % user_id, msgDone)

@confirmation_required(lambda user_id=None, address_id=None : str(get_object_or_404(Address, pk=address_id)), 'manage/base.html', _('Do you really want to delete your address'))
@login_required
def user_address_delete(request, user_id=None, address_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    return ain7_generic_delete(request,
        get_object_or_404(Address, pk=address_id),
        '/manage/users/%s/edit/#address' % user_id,
        _('Address successfully deleted.'))

# Numeros de telephone
@login_required
def user_phone_edit(request, user_id=None, phone_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    person = get_object_or_404(Person, user=user_id)
    phone = None
    title = _('Creation of a phone number for')
    msgDone = _('Phone number added successfully.')
    if phone_id:
        phone = get_object_or_404(PhoneNumber, pk=phone_id)
        title = _('Modification of a phone number for')
        msgDone = _('Phone number informations updated successfully.')
    return ain7_generic_edit(
        request, phone, PhoneNumberForm, {'person': person},
        'manage/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/manage/users/%s/edit/#phone' % user_id, msgDone)

@confirmation_required(lambda user_id=None, phone_id=None : str(get_object_or_404(PhoneNumber, pk=phone_id)), 'manage/base.html', _('Do you really want to delete your phone number'))
@login_required
def user_phone_delete(request, user_id=None, phone_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    return ain7_generic_delete(request,
        get_object_or_404(PhoneNumber, pk=phone_id),
        '/manage/users/%s/edit/#phone' % user_id,
        _('Phone number successfully deleted.'))

# Adresses de courriel
@login_required
def user_email_edit(request, user_id=None, email_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    person = get_object_or_404(Person, user=user_id)
    email = None
    title = _('Creation of an email address for')
    msgDone = _('Email address successfully added.')
    if email_id:
        email = get_object_or_404(Email, pk=email_id)
        title = _('Modification of an email address for')
        msgDone = _('Email informations updated successfully.')
    return ain7_generic_edit(
        request, email, EmailForm, {'person': person},
        'manage/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/manage/users/%s/edit/#email' % user_id, msgDone)

@confirmation_required(lambda user_id=None, email_id=None : str(get_object_or_404(Email, pk=email_id)), 'manage/base.html', _('Do you really want to delete your email address'))
@login_required
def user_email_delete(request, user_id=None, email_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    return ain7_generic_delete(request, get_object_or_404(Email, pk=email_id),
                               '/manage/users/%s/edit/#email' % user_id,
                               _('Email address successfully deleted.'))

@login_required
def nationality_add(request):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    form = NewCountryForm()

    if request.method == 'POST':
        form = NewCountryForm(request.POST)
        if form.is_valid():

            if not Country.objects.filter(name=form.cleaned_data['name']).count() == 0:
                request.user.message_set.create(message=_("Several countries have the same name. Please choose another one"))

            else:
                new_role = form.save()
                request.user.message_set.create(
                    message=_("New country successfully created"))
                return ain7_render_to_response(request, 'pages/frame_message.html', {})

        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'pages/frame_edit_form.html',
        {'action_title': _('Register new country'), 'back': back, 'form': form})

@login_required
def jobs_proposals(request):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r
    return ain7_render_to_response(request, 'manage/job_proposals.html',
        {'proposals': JobOffer.objects.filter(checked_by_secretariat=False)})

@confirmation_required(lambda job_id=None: str(get_object_or_404(JobOffer, pk=job_id)), 'manage/base.html', _('Do you confirm the validation of this job proposal'))
@login_required
def job_validate(request, job_id=None):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r
    job = get_object_or_404(JobOffer, pk=job_id)
    # validate
    job.checked_by_secretariat = True
    job.save()
    request.user.message_set.create(
        message=_("Job proposal validated."))
    # remove notification
    notif = job.notification.all()
    if notif:
        notif[0].delete()
        request.user.message_set.create(
            message=_("Corresponding notification removed."))
    return HttpResponseRedirect('/manage/jobs/proposals/')

@confirmation_required(lambda job_id=None: str(get_object_or_404(JobOffer, pk=job_id)), 'manage/base.html', _('Do you really want to delete this job proposal'))
@login_required
def job_delete(request, job_id=None):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r
    job = get_object_or_404(JobOffer, pk=job_id)
    # remove notification
    notif = job.notification.all()
    if notif:
        notif[0].delete()
        request.user.message_set.create(
            message=_("Corresponding notification removed."))
    # validate
    job.delete()
    request.user.message_set.create(
        message=_("Job proposal removed."))
    return HttpResponseRedirect('/manage/jobs/proposals/')

def errors_index(request):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    nb_results_by_page = 25 
    errors = PortalError.objects.all()
    paginator = Paginator(errors, nb_results_by_page)
    try:
         page = int(request.GET.get('page', '1'))
         errors = paginator.page(page).object_list
    except InvalidPage:
         raise http.Http404

    return ain7_render_to_response(request, 'manage/errors_index.html',
        {'errors': errors, 'request': request,
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.num_pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count})

@login_required
def error_details(request, error_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    e = get_object_or_404(PortalError, pk=error_id)
    return ain7_render_to_response(
        request, 'manage/error_details.html', {'error': e})
