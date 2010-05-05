# -*- coding: utf-8
"""
 ain7/groupes_professionnels/urls.py
"""
#
#   Copyright © 2007-2010 AIn7 Devel Team
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

from django.conf.urls.defaults import patterns


urlpatterns = patterns('ain7.groupes_professionnels.views',
    # Groupes
    (r'^$', 'index'),
    (r'^(?P<group_name>\w+)/$', 'details'),
    (r'^(?P<group_name>\w+)/edit/$', 'edit'),
    (r'^(?P<group_name>\w+)/subscribe/$', 'subscribe'),
    (r'^(?P<group_name>\w+)/unsubscribe/$', 'unsubscribe'),
    (r'^(?P<group_name>\w+)/roles/edit/(?P<all_current>\w+)/$', 'edit_roles'),
    (r'^(?P<group_name>\w+)/roles/(?P<role_id>\d+)/changedates/'
     +r'(?P<all_current>\w+)/$', 'change_dates'),
    (r'^(?P<group_name>\w+)/roles/(?P<type>\d+)/add/(?P<all_current>\w+)/$',
         'add_role'),
    (r'^(?P<group_name>\w+)/roles/(?P<role_id>\d+)/delete/'
     +r'(?P<all_current>\w+)/$', 'delete_role'),

)
