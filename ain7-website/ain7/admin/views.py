# -*- coding: utf-8
#
# admin/views.py
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

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission, User
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms
from django.http import HttpResponseRedirect, HttpResponse

from ain7.utils import ain7_render_to_response
from ain7.annuaire.models import Person

from ain7.fields import AutoCompleteField

@login_required
def index(request):
    return ain7_render_to_response(request, 'admin/default.html', {})

class SearchPersonForm(forms.Form):
    last_name = forms.CharField(label=_('Last name'), max_length=50, required=False)
    first_name = forms.CharField(label=_('First name'), max_length=50, required=False)

class SearchGroupForm(forms.Form):
    name = forms.CharField(label=_('Name'), max_length=50, required=False)

class PermGroupForm(forms.Form):
    perm = forms.CharField(label=_('Permission'), max_length=50, required=True)

class MemberGroupForm(forms.Form):
    username = forms.CharField(label=_('Username'), max_length=100, required=True, widget=AutoCompleteField(url='/ajax/person/'))

@login_required
def users_search(request):

    form = SearchPersonForm()
    nb_results_by_page = 25
    persons = False
    paginator = ObjectPaginator(Group.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchPersonForm(request.POST)
        if form.is_valid():

            # criteres sur le nom et prenom
            criteria={'last_name__contains':form.clean_data['last_name'].encode('utf8'),\
                      'first_name__contains':form.clean_data['first_name'].encode('utf8')}

            persons = Person.objects.filter(**criteria)
            paginator = ObjectPaginator(persons, nb_results_by_page)

            try:
                page = int(request.GET.get('page', '1'))
                persons = paginator.get_page(page - 1)

            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'admin/users_search.html',
                            {'form': form, 'persons': persons,'paginator': paginator, 'is_paginated': paginator.pages > 1,
                             'has_next': paginator.has_next_page(page - 1),
                             'has_previous': paginator.has_previous_page(page - 1),
                             'current_page': page,
                             'next_page': page + 1,
                             'previous_page': page - 1,
                             'pages': paginator.pages,
                             'first_result': (page - 1) * nb_results_by_page +1,
                             'last_result': min((page) * nb_results_by_page, paginator.hits),
                             'hits' : paginator.hits,})

@login_required
def groups_search(request):

    form = SearchGroupForm()
    nb_results_by_page = 25
    groups = False
    paginator = ObjectPaginator(Group.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchGroupForm(request.POST)
        if form.is_valid():

            # criteres sur le nom et prenom
            criteria={'name__contains':form.clean_data['name'].encode('utf8')}

            print form.clean_data['name']

            groups = Group.objects.filter(**criteria)
            paginator = ObjectPaginator(groups, nb_results_by_page)

            try:
                page = int(request.GET.get('page', '1'))
                groups = paginator.get_page(page - 1)

            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'admin/groups_search.html',
                            {'form': form, 'groups': groups,'paginator': paginator, 'is_paginated': paginator.pages > 1,
                    'has_next': paginator.has_next_page(page - 1),
                    'has_previous': paginator.has_previous_page(page - 1),
                    'current_page': page,
                    'next_page': page + 1,
                    'previous_page': page - 1,
                    'pages': paginator.pages,
                    'first_result': (page - 1) * nb_results_by_page +1,
                    'last_result': min((page) * nb_results_by_page, paginator.hits),
                    'hits' : paginator.hits,})

@login_required
def group_details(request, group_id):
    g = get_object_or_404(Group, pk=group_id)
    return ain7_render_to_response(request, 'admin/group_details.html', {'group': g})

@login_required
def perm_add(request, group_id):
    g = get_object_or_404(Group, pk=group_id)

    form = PermGroupForm()

    if request.method == 'POST':
        form = PermGroupForm(request.POST)
        if form.is_valid():
            p = Permission.objects.filter(name=form.clean_data['perm'])[0]
            g.permissions.add(p)
            request.user.message_set.create(message=_('Permission added to group'))
            return HttpResponseRedirect('/admin/groups/%s/' % group_id)
        else:
            request.user.message_set.create(message=_('Permission is not correct'))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request, 'admin/groups_perm_add.html',
                            {'form': form, 'group': g, 'back': back})

@login_required
def perm_delete(request, group_id, perm_id):
    group = get_object_or_404(Group, pk=group_id)
    perm = get_object_or_404(Permission, pk=perm_id)

    group.permissions.remove(perm)

    request.user.message_set.create(message=_('Permission removed from group'))

    return HttpResponseRedirect('/admin/groups/%s/' % group_id)

@login_required
def member_add(request, group_id):

    g = get_object_or_404(Group, pk=group_id)

    form = MemberGroupForm()

    if request.method == 'POST':
        form = MemberGroupForm(request.POST)
        if form.is_valid():
            print form.clean_data['username']
            u = User.objects.filter(id=form.clean_data['username'])[0]
            u.groups.add(g)
            request.user.message_set.create(message=_('User added to group'))
            return HttpResponseRedirect('/admin/groups/%s/' % group_id)
        else:
            request.user.message_set.create(message=_('User is not correct'))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request, 'admin/groups_user_add.html',
                            {'form': form, 'group': g, 'back': back})

@login_required
def member_delete(request, group_id, member_id):
    group = get_object_or_404(Group, pk=group_id)
    member = get_object_or_404(User, pk=member_id)

    member.groups.remove(group)

    request.user.message_set.create(message=_('Member removed from group'))

    return HttpResponseRedirect('/admin/groups/%s/' % group_id)

@login_required
def permissions(request):

    nb_results_by_page = 25

    permissions = Permission.objects.all()
    paginator = ObjectPaginator(Permission.objects.all(), nb_results_by_page)

    try:
        page = int(request.GET.get('page', '1'))
        permissions = paginator.get_page(page - 1)

    except InvalidPage:
        raise http.Http404

    return ain7_render_to_response(request, 'admin/permissions.html', {'permissions': permissions, 'paginator': paginator, 'is_paginated': paginator.pages > 1,
            'has_next': paginator.has_next_page(page - 1),
            'has_previous': paginator.has_previous_page(page - 1),
            'current_page': page,
            'next_page': page + 1,
            'previous_page': page - 1,
            'pages': paginator.pages,
            'first_result': (page - 1) * nb_results_by_page +1,
            'last_result': min((page) * nb_results_by_page, paginator.hits),
            'hits' : paginator.hits,})

@login_required
def permission_details(request, perm_id):

    permission = get_object_or_404(Permission, pk=perm_id)

    return ain7_render_to_response(request, 'admin/permission_details.html', {'permission': permission})
