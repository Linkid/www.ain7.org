# -*- coding: utf-8
"""
 ain7/evenements/urls.py
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


urlpatterns = patterns('ain7.evenements.views',
    # Evenements
    (r'^$', 'index'),
    (r'^ical/$', 'ical'),
    (r'^new/$', 'add'),
    (r'^search/$', 'search'),
    (r'^(?P<event_id>\d+)/$', 'details'),
    (r'^(?P<event_id>\d+)/edit/$', 'edit'),
    (r'^(?P<event_id>\d+)/image/delete/$', 'image_delete'),
#    (r'^(?P<event_id>\d+)/join/$', 'join'),
    (r'^(?P<event_id>\d+)/contact/$', 'contact'),
#    (r'^(?P<event_id>\d+)/participants/$', 'participants'),
#    (r'^(?P<event_id>\d+)/subscribe/$', 'subscribe'),
    (r'^(?P<event_id>\d+)/organizer/add/$', 'organizer_add'),
    (r'^(?P<event_id>\d+)/organizer/(?P<organizer_id>\d+)/delete/$',
        'organizer_delete'),
    (r'^(?P<event_id>\d+)/organizer/(?P<organizer_id>\d+)/swap_email_notif/$',
        'swap_email_notif'),

)
