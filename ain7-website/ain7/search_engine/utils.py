# -*- coding: utf-8 -*-
#
# search_engine/utils.py
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

import time
import datetime

from django import forms
from django.db import models
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404

from ain7.widgets import DateTimeWidget
from ain7.ajax.views import ajaxed_fields
from ain7.search_engine.models import *
from ain7.fields import AutoCompleteField


# for each type of attribute, we define the comparators and the
# type of field to display in the form
dateWidget = DateTimeWidget()
dateWidget.dformat = '%d/%m/%Y'
dateTimeWidget = DateTimeWidget()
dateTimeWidget.dformat = '%d/%m/%Y %H:%M'
FIELD_PARAMS = [
    ('CharField',
     [('EQ',_('equals'),    '__iexact',   False),
      ('NE',_('not equals'),'__iexact',   True ),
      ('CT',_('contains'),  '__icontains',False)],
     forms.CharField(label='')),
    ('TextField',
     [('EQ',_('equals'),    '__iexact',   False),
      ('NE',_('not equals'),'__iexact',   True ),
      ('CT',_('contains'),  '__icontains',False)],
     forms.CharField(label='')),
    ('DateField',
     [('EQ',_('equals'),'',     False),
      ('BF',_('before'),'__lte',False),
      ('AT',_('after'), '__gte',False),],
     forms.DateField(label='', widget=dateWidget)),
    ('DateTimeField',
     [('EQ',_('equals'),'',     False),
      ('BF',_('before'),'__lte',False),
      ('AT',_('after'), '__gte',False),],
     forms.DateTimeField(label='', widget=dateTimeWidget)),
    ('IntegerField',
     [('EQ',_('equals'),    '__exact', False),
      ('NE',_('not equals'),'__exact', True ),
      ('LT',_('lower'),     '__lt',    False),
      ('GT',_('greater'),   '__gt',    False),],
     forms.IntegerField(label='')),
    ('BooleanField',
     [('IS',_('is'),'',False)],
     forms.BooleanField(label='', required=False, initial=True)),
    # for ForeignKey, the field is defined later
    ('ForeignKey',
     [('EQ',_('equals'),    '__exact', False),
      ('NE',_('not equals'),'__exact', True )],
     None),
    # for ManyToManyField, the field is defined later
    ('ManyToManyField',
     [('EQ',_('equals'),    '__exact', False),
      ('NE',_('not equals'),'__exact', True )],
     None),

    # Not implemented: RelatedField
    
    # Not implemented because not used in our model
    # or meaningless for a search engine:
    # AutoField, DecimalField, EmailField(CharField), FileField,
    # FilePathField, FloatField, ImageField(FileField), IPAddressField,
    # NullBooleanField, PhoneNumberField(IntegerField),
    # PositiveIntegerField(IntegerField),
    # PositiveSmallIntegerField(IntegerField), SlugField(CharField),
    # SmallIntegerField(IntegerField), TimeField, URLField(CharField),
    # USStateField(Field), XMLField(TextField),
    # OrderingField(IntegerField)
    ]

def getFieldFromName(fieldClass, fieldName, search_engine):
    """ Returns a field from its class and its name."""
    field = None
    # first we look into models for which all fields are criteria
    for basicField in fieldClass._meta.fields:
        if fieldName == basicField.name:
            field = basicField
    if fieldClass._meta.many_to_many:
        for manyToManyField in fieldClass._meta.many_to_many:
            if fieldName == manyToManyField.name:
                field = manyToManyField
    # then we look for fields manually managed
    for (fName, fModel, comps) in params(search_engine).custom_fields:
        if fieldName == fName:
            field = getModelField(fModel, fName)
    return field

def getModelField(fModel, fName):
    """ Given a model and the name of one of its fields, returns this field."""
    field = None
    for f in fModel._meta.fields:
        if f.name == fName:
            field = f
    return field

def compInQ(fieldClass, fieldName,compCode, search_engine):
    field = getFieldFromName(fieldClass, fieldName, search_engine)
    fieldName, comps, formField = findParamsForField(field)
    if comps == None:
        raise NotImplementedError
    for compName, compVN, qComp, qNeg in comps:
        if compName == compCode:
            return (qComp,qNeg)
    return None

def findParamsForField(field):
    for fieldName, comps, formField in FIELD_PARAMS:
        if str(type(field)).find(fieldName)!=-1:
            return (fieldName, comps, formField)
    raise NotImplementedError
    return None

def splitFieldFullname(fModelAndName):
    """Example:
    'annuaire.person.last_name' -> ('annuaire.person','last_name')"""
    pointPos = fModelAndName.rindex('.')
    fModel = fModelAndName[:pointPos]
    fName = fModelAndName[pointPos+1:]
    return fModel, fName

def criteriaList(search_engine, user):
    """ Returns the list of fields that are criteria for an advanced
    search.
    These fields are the attributes of models of CRITERIA_MODELS.
    If the user has an admin profile, he gets all these attributes,
    except OneToOne and ImageField fields.
    If not, we also exclude the fields of EXCLUDE_FIELDS."""

    attrList = []

    # models for which attributes are criteria for advanced search
    for model in params(search_engine).criteria_models.keys():

        for field in model._meta.fields + model._meta.many_to_many:

            if field.name in model.objects.adv_search_fields(user)\
                and (str(type(field)).find('OneToOneField')==-1)\
                and not isinstance(field,models.FileField):
                attrList.append((field,model))

    # now we deal with custom fields
    for (fName,fModel,query) in params(search_engine).custom_fields:
        attrList.append((getModelField(fModel, fName),fModel))

    # uncomment this if you want a sorted list of criteria
    #
    # def cmpFields(field1, field2):
    #     return cmp(field1.verbose_name.capitalize(),
    #                field2.verbose_name.capitalize())
    # attrList.sort(cmpFields)

    return attrList

def filtersToExclude(filter_id=None):
    """ A recursive function that computes filters to exclude
    when proposing the user a list of filters as criteria for the
    filter given in parameter. This corresponds to the filter itself
    and to every filter having this filter as criterion."""
    if filter_id==None:
        return []
    else:
        filtr = get_object_or_404(SearchFilter, pk=filter_id)
        result = [ filter_id ]        
        for crit in filtr.used_as_criterion.all():
            result.extend(filtersToExclude(crit.searchFilter.id))
        return result

def findComparatorsForField(field, parameters):
    """ Returns the set of comparators for a given field,
    depending on its type."""
    compList = None
    formField = None
    (fieldName, comps, formField) = findParamsForField(field)
    if comps == None:
        raise NotImplementedError
    choiceList = []
    for compName, compVN, qComp, qNeg in comps:
        choiceList.append((compName,compVN))
    # if there is a choice list in the model, use it (for instance Person.sex)
    if '_choices' in field.__dict__ and field.__dict__['_choices'] != []:
        formField = forms.ChoiceField(
            label='', choices=field.__dict__['_choices'])
    # if it's an ajaxed field, we use autocompletion.
    # ajaxed fields are supposed to be ForeignKeys or ManyToMany fields.
    ajax_dict = ajaxed_fields()
    if field.rel and field.rel.to in ajax_dict:
        field_url = '/ajax/' + ajax_dict[field.rel.to] + '/'
        formField = forms.CharField(
            label='', widget=AutoCompleteField(url=field_url))
    return (choiceList,formField)

def getDisplayedVal(value, fieldClass, fieldName, search_engine):
    """ Converts a value obtained from the form
    to a format displayed in the criteria list. """
    displayedVal = value
    field = getFieldFromName(fieldClass, fieldName, search_engine)
    if str(type(field)).find('DateField')!=-1:
        dateVal = datetime.datetime(
            *time.strptime(str(value),'%Y-%m-%d')[0:5])
        displayedVal = dateVal.strftime('%d/%m/%Y')
    if str(type(field)).find('DateTimeField')!=-1:
        dateVal = datetime.datetime(
            *time.strptime(str(value),'%Y-%m-%d %H:%M:%S')[0:5])
        displayedVal = dateVal.strftime('%d/%m/%Y %H:%M')
    if str(type(field)).find('BooleanField')!=-1:
        if value:
            displayedVal = _('checked')
        else:
            displayedVal = _('unchecked')
    if '_choices' in field.__dict__:
        # in this case we used a ChoiceField and stored a key, not a value
        for (k,v) in field.__dict__['_choices']:
            if str(k)==value: displayedVal = v                
    # if it's an ajaxed field, we store the id,
    # as ajaxed fields are supposed to be ForeignKeys or ManyToManyFields
    if field.rel and field.rel.to in ajaxed_fields():
        obj = get_object_or_404(field.rel.to, pk=value)
        displayedVal = str(obj)
    return displayedVal

def getCompVerboseName(field, compCode):
    """ Returns the description of a comparator,
    given the field and the comparator's code."""
    compVerbName = None
    (fieldName, comps, formField) = findParamsForField(field)
    for code, name, qComp, qNeg in comps:
        if code == compCode:
            compVerbName = name
    return compVerbName


