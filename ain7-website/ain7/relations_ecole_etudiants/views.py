# -*- coding: utf-8
#
# relations_ecoles_etudiants/views.py
#
#   Copyright © 2007-2009 AIn7 Devel Team
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

from ain7.pages.models import Text
from ain7.utils import ain7_render_to_response


def index(request): 
    text = Text.objects.get(textblock__shortname='relations_ecole_etudiants')
    return ain7_render_to_response(request, 
                'relations_ecole_etudiants/index.html', {'text': text})

