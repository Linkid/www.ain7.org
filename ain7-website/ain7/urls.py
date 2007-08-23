# -*- coding: utf-8
#
# urls.py
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

import os.path

from django.conf.urls.defaults import *

from ain7.feeds import LatestEvents, LatestEntriesByCategory

feeds = {
    'events': LatestEvents,
    'categories': LatestEntriesByCategory,
}

urlpatterns = patterns('',

    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
#    (r'^accounts/logout/$', 'ain7.utils.logout'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),

    # servir le contenu statique pendant le dev
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.abspath(os.path.dirname(__file__))+'/media'}),

    # Uncomment this for admin:
    (r'^dadmin/', include('django.contrib.admin.urls')),

    # AIn7 admin section
    (r'^admin/', include('ain7.admin.urls')),

    # annuaire
    (r'^annuaire/', include('ain7.annuaire.urls')),

    # emploi
    (r'^emploi/', include('ain7.emploi.urls')),

    # news
    (r'^actualites/', include('ain7.news.urls')),

    # evenements
    (r'^evenements/', include('ain7.evenements.urls')),

    # groupes
    (r'^groupes/', include('ain7.groupes.urls')),

    # groupes regionaux
    (r'^groupes_regionaux/', include('ain7.groupes_regionaux.urls')),

    # sondage
    (r'^sondages/', include('ain7.sondages.urls')),

    # voyages
    (r'^voyages/', include('ain7.voyages.urls')),

    # planet
    (r'^planet/', 'ain7.utils.planet'),

    # forums
    (r'^forums/', 'ain7.utils.forums'),

    # Pages particulieres au contenu pseudo statique
    (r'^apropos/','ain7.pages.views.apropos'),
    (r'^association/','ain7.pages.views.association'),
    (r'^canal_n7/','ain7.pages.views.canal_n7'),
    (r'^contact/','ain7.pages.views.contact'),
    (r'^international/','ain7.pages.views.international'),
    (r'^mentions_legales/','ain7.pages.views.mentions_legales'),
    (r'^publications/','ain7.pages.views.publications'),
    (r'^sitemap/','ain7.pages.views.sitemap'),
    (r'^$','ain7.pages.views.homepage'),

    # flux RSS
    (r'^rss/$', 'ain7.pages.views.rss'),
    (r'^rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),

)
