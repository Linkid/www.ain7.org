# -*- coding: utf-8
#
# manage/models.py
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

import datetime

from django.db import models
from django.utils.translation import ugettext as _

from ain7.emploi.models import ACTIONS, OrganizationProposal, OfficeProposal

# A notification
class Notification(models.Model):

    PROPOSAL_TYPE = (
        (0, _('organization')),
        (1, _('office')),
        )

    title = models.CharField(verbose_name=_('title'), max_length=50)
    details = models.TextField(verbose_name=_('Notes'),
        blank=True, null=True)
    organization_proposal = models.ForeignKey(
        OrganizationProposal, verbose_name=_('organization proposal'),
        blank=True, null=True)
    office_proposal = models.ForeignKey(
        OfficeProposal, verbose_name=_('organization proposal'),
        blank=True, null=True)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)
    modifier = models.IntegerField(editable=False)

    def __unicode__(self):
        return self.title

    def save(self):
        self.modification_date = datetime.datetime.today()
        self.modifier = 1 # TODO
        return super(Notification, self).save()

    class Admin:
        pass

    class Meta:
        verbose_name = _('notification')

