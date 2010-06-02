#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Datastore models.
# Copyright (c) 2009, 2010 happychickoo.
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import configuration

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from dbhelper import SerializableModel
from pytz.gae import pytz
from countries import ISO_ALPHA_3_CODES
from aetycoon import DerivedProperty

TIMEZONE_CHOICES = pytz.all_timezones
DEFAULT_TIMEZONE_CHOICE = configuration.DEFAULT_TIMEZONE


COUNTRY_CODE_CHOICES = ISO_ALPHA_3_CODES
DEFAULT_COUNTRY_CODE_CHOICE = 'IND'


RELATIONSHIP_STATUS_CHOICES = (
    'married',
    'single',
    'committed',
    'other',
)
DEFAULT_RELATIONSHIP_STATUS_CHOICE = 'single'


GENDER_TYPES = dict(
    male='Male',
    female='Female',
)
GENDER_TYPES_TUPLE_MAP = [(k, v) for k, v in GENDER_TYPES.iteritems()]
GENDER_CHOICES = GENDER_TYPES.keys()
DEFAULT_GENDER_CHOICE = 'male'


ADDRESS_TYPE_CHOICES = (
    'home',
    'work',
    'correspondence',
    'other',
)
DEFAULT_ADDRESS_TYPE_CHOICE = 'home'


PHONE_TYPES = dict(
    mobile='Mobile',
    work_mobile='Work Mobile',
    home='Home',
    work='Work',
    fax='Fax',
    work_fax='Work Fax',
    pager='Pager',
    work_pager='Work Pager',
    callback='Callback',
    telex='Telex',
    car='Car',
    company_main='Company Main',
    other='Other',
    isdn='ISDN',
)
PHONE_TYPES_TUPLE_MAP = [(k, v) for k, v in PHONE_TYPES.iteritems()]
PHONE_TYPE_CHOICES = PHONE_TYPES.keys()
PHONE_TYPE_CHOICES.sort()
DEFAULT_PHONE_TYPE_CHOICE = 'mobile'


EMAIL_TYPE_CHOICES = (
    'home',
    'work',
    'mobile',
    'other',
)
DEFAULT_EMAIL_TYPE_CHOICE = 'home'


PAYMENT_MODE_CHOICES = (
    'electronic',
    'cheque',
    'cash',
)
DEFAULT_PAYMENT_MODE_CHOICE = 'electronic'


T_SHIRT_SIZES = {
    'small': 'Small',
    'medium': 'Medium',
    'large': 'Large',
    'extra_large': 'Extra Large',
}
T_SHIRT_SIZES_TUPLE_MAP = [(k, v) for k, v in T_SHIRT_SIZES.iteritems()]
T_SHIRT_SIZE_CHOICES = T_SHIRT_SIZES.keys()
T_SHIRT_SIZE_CHOICES.sort()


RAILWAY_LINES = {
    'western': 'Western',
    'central': 'Central',
    'harbor': 'Harbor',
    'other': 'Out of Mumbai',
}
RAILWAY_LINES_TUPLE_MAP = [(k, v) for k, v in RAILWAY_LINES.iteritems()]
RAILWAY_LINE_CHOICES = [k for k, v in RAILWAY_LINES.iteritems()]
RAILWAY_LINE_CHOICES.sort()
DEFAULT_RAILWAY_LINE_CHOICE = 'western'


class Profile(polymodel.PolyModel):
    """
    Base polymodel which is bound to all the contact information
    irrespective of the type of profile.
    """
    user = db.UserProperty()
    when_created = db.DateTimeProperty(auto_now_add=True)
    when_modified = db.DateTimeProperty(auto_now=True)
    timezone = db.StringProperty(choices=TIMEZONE_CHOICES, default=DEFAULT_TIMEZONE_CHOICE)
    # Profiles are activated by the administrator.
    is_active = db.BooleanProperty(default=False)
    
    def activate(self):
        from utils import queue_mail_task
        
        self.is_active = True
        self.put()
        
        queue_mail_task(
            url='/worker/mail/activate-account',
            params=dict(
                profile_key=unicode(self.key()),
            ),
            method='POST'
        )
    
    
    def email_addresses_list(self):
        return [unicode(e.email) for e in self.email_addresses]
    
    
    def phones_list(self):
        return [p.number for p in self.phones]


class Phone(SerializableModel):
    """
    Records phone numbers belonging to a profile.
    """
    profile = db.ReferenceProperty(Profile, collection_name='phones')
    phone_type = db.StringProperty(choices=PHONE_TYPE_CHOICES, default=DEFAULT_PHONE_TYPE_CHOICE)
    number = db.StringProperty(required=True)


class EmailAddress(SerializableModel):
    """
    Records email addresses belonging to a profile.
    """
    profile = db.ReferenceProperty(Profile, collection_name='email_addresses')
    email_type = db.StringProperty(choices=EMAIL_TYPE_CHOICES, default=DEFAULT_EMAIL_TYPE_CHOICE)
    email = db.EmailProperty(required=True)


class Host(SerializableModel):
    """
    Stores host information about a profile browsing
    the Website.  We use this information to determine
    what people use for browsing and where they are usually
    located.
    """
    profile = db.ReferenceProperty(Profile, collection_name='hosts')
    ip_address = db.StringProperty()
    http_user_agent = db.StringProperty()
    http_accept_language = db.StringProperty()
    http_accept_charset = db.StringProperty()
    http_accept_encoding = db.StringProperty()
    http_accept = db.StringProperty()
    http_referrer = db.StringProperty()


class Person(Profile):
    """
    Personal information.

    Helps answer these questions:

    1. What is the name of the person?
    2. When did the person register?
    3. Which IP addresses and locations has the person been browsing from?
    """
    honorary_prefix = db.StringProperty()
    honorary_suffix = db.StringProperty()

    first_name = db.StringProperty(required=True)
    last_name = db.StringProperty(required=True)
    birthdate = db.DateProperty()
    t_shirt_size = db.StringProperty(choices=T_SHIRT_SIZE_CHOICES)
    gender = db.StringProperty(choices=GENDER_CHOICES)
    graduation_year = db.IntegerProperty()
    relationship_status = db.StringProperty(choices=RELATIONSHIP_STATUS_CHOICES, default=DEFAULT_RELATIONSHIP_STATUS_CHOICE)
    is_student = db.BooleanProperty(default=False)


    @DerivedProperty
    def marital_prefix(self):
        if self.gender == 'female':
            if self.relationship_status == 'married':
                return 'Mrs.'
            else:
                return 'Miss'
        else:
            return 'Mr.'


    @DerivedProperty
    def full_name(self):
        return unicode(self.first_name + ' ' + self.last_name)


    @DerivedProperty
    def honorary_name(self):
        if self.honorary_prefix:
            honorary_prefix = self.honorary_prefix + ' '
        else:
            honorary_prefix = ''
        if self.honorary_suffix:
            honorary_suffix = ', ' + self.honorary_suffix
        else:
            honorary_suffix = ''
        return unicode(honorary_prefix + self.marital_prefix + ' ' + self.full_name +  honorary_suffix)


    def __unicode__(self):
        return self.full_name


    def __str__(self):
        return self.__unicode__()


class WorkProfile(SerializableModel):
    """
    Work profile of a person.
    """
    designation = db.StringProperty()
    company = db.StringProperty()
    person = db.ReferenceProperty(Person, collection_name='work_profiles')


    def __unicode__(self):
        return self.designation + ', ' + self.company


    def __str__(self):
        return self.__unicode__()


class Location(SerializableModel):
    """
    Address locations for a profile.
    """
    profile = db.ReferenceProperty(Profile, collection_name='locations')
    state_or_province = db.StringProperty()
    street_name = db.StringProperty()
    city = db.StringProperty()
    zip_code = db.StringProperty()
    nearest_railway_line = db.StringProperty(choices=RAILWAY_LINE_CHOICES, default=DEFAULT_RAILWAY_LINE_CHOICE)
    country_code = db.StringProperty(choices=COUNTRY_CODE_CHOICES, default=DEFAULT_COUNTRY_CODE_CHOICE)


    @DerivedProperty
    def country_name(self):
        from countries import COUNTRY_NAME_ISO_ALPHA_3_TABLE as table
        return table.get(self.country_code)


    @DerivedProperty
    def postal_address(self):
        return ', '.join([self.street_name, self.city, self.state_or_province, self.zip_code, self.country_name])


    def __unicode__(self):
        return self.postal_address


    def __str__(self):
        return self.__unicode__()


class Post(SerializableModel):
    path = db.StringProperty()
    checksum = db.StringProperty()
    title = db.StringProperty()
    is_published = db.BooleanProperty(default=False)
    when_published = db.DateTimeProperty()
    content = db.TextProperty()
    content_html = db.TextProperty()
    
    @property
    def rendered(self):
        pass #return render_markup(self.content)
    
    def __unicode__(self):
        return self.rendered
