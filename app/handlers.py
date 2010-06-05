#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Website URL handlers.
# Copyright (c) 2009 happychickoo.
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
import logging

from google.appengine.api import users, memcache
from google.appengine.ext import db, ereporter
from google.appengine.ext.webapp.util import run_wsgi_app, login_required
from tornado.wsgi import WSGIApplication
from utils import BaseRequestHandler, SessionRequestHandler, send_mail_once
from models import Profile
from countries import COUNTRY_ISO_ALPHA_TABLE, COUNTRIES_LIST
try:
    import json
except ImportError:
    from django.utils import simplejson as json


logging.basicConfig(level=logging.DEBUG)

ereporter.register_logger()

class IndexHandler(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            identity = user.federated_identity()
            if identity and Profile.get_by_key_name(identity):
                self.redirect('/blog')
            else:
                self.redirect('/register')
        else:
            self.render('index.html', 
                video_url=configuration.INTRO_VIDEO_URL, 
                login_url='/login')


class LoginHandler(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect('/profile')
        else:
            self.render('login.html')
        
    def post(self):
        federated_identity = self.get_argument('openid_identifier')
        logging.info(federated_identity)        
        profile = Profile.get_by_key_name(federated_identity)
        if profile:
            dest_url = '/blog'
        else:
            dest_url = '/register'
        login_url = users.create_login_url(dest_url=dest_url, federated_identity=federated_identity)
        self.redirect(login_url)


class LogoutHandler(BaseRequestHandler):
    @login_required
    def get(self):
        self.redirect(users.create_logout_url(dest_url='/'))


class BlogHandler(BaseRequestHandler):
    @login_required
    def get(self):
        self.render('blog.html', logout_url=users.create_logout_url('/'))


class RegisterHandler(BaseRequestHandler):
    @login_required
    def get(self):
        from models import DEFAULT_COUNTRY_CODE_CHOICE, GENDER_TYPES_TUPLE_MAP, T_SHIRT_SIZES_TUPLE_MAP, RAILWAY_LINES_TUPLE_MAP, DEFAULT_RAILWAY_LINE_CHOICE, DEFAULT_PHONE_TYPE_CHOICE, PHONE_TYPES_TUPLE_MAP
        from pytz.gae import pytz
        from services import country_code_from_ip_address
        
        user = users.get_current_user()
        federated_identity = user.federated_identity()
        email = user.email()
        logging.info('Email: ' + email)
        logging.info("Federated identity: " + str(federated_identity))
        
        determined_country_code = country_code_from_ip_address(self.request.remote_ip)
        if determined_country_code.lower() == 'zz':
            determined_country_code = 'IN'
        country_code = COUNTRY_ISO_ALPHA_TABLE.get(determined_country_code)
        timezones = pytz.country_timezones(determined_country_code)
        railway_line_choice = DEFAULT_RAILWAY_LINE_CHOICE
        city = 'Mumbai'
        state_or_province = 'Maharashtra'
        if country_code != 'IND':
            railway_line_choice = 'other'
            city = ''
            state_or_province = ''
        self.render('register.html', 
            email=email,
            gender_choices=GENDER_TYPES_TUPLE_MAP,
            t_shirt_sizes=T_SHIRT_SIZES_TUPLE_MAP,
            railway_lines=RAILWAY_LINES_TUPLE_MAP,
            countries_list=COUNTRIES_LIST,
            phone_types=PHONE_TYPES_TUPLE_MAP,
            timezones=timezones,
            state_or_province=state_or_province,
            city=city,
            default_phone_type=DEFAULT_PHONE_TYPE_CHOICE,
            default_country_code=country_code,
            default_railway_line_choice=railway_line_choice,
            federated_identity=federated_identity,
            logout_url=users.create_logout_url('/'))
    
    def post(self):
        logging.info(self.request.arguments)


class ProfileHandler(BaseRequestHandler):
    @login_required
    def get(self):
        self.render('profile.html', logout_url=users.create_logout_url('/'))


class AboutHandler(BaseRequestHandler):
    @login_required
    def get(self):
        self.render('about.html', logout_url=users.create_logout_url('/'))


# Api
class ApiTimezonesForCountryCodeHandler(BaseRequestHandler):
    def get(self, country_code='IND'):
        cache_key = 'timezones_for_country_code_%s' % country_code
        timezones = memcache.get(cache_key)
        if timezones is None:
            from pytz.gae import pytz
            alpha2_code = COUNTRY_ISO_ALPHA_TABLE.get(country_code, 'IN')
            timezones = pytz.country_timezones(alpha2_code)
            timezones.sort()
            memcache.set(cache_key, timezones)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(timezones))

# Workers
class WorkerMailActivateAccountHandler(BaseRequestHandler):
    def post(self):
        profile_key = self.get_argument('profile_key')
        profile = db.get(db.Key(profile_key))
        body = self.render_string('email/activate-account.txt', profile=profile)
        send_mail_once(
            cache_key='@' + self.__class__.__name__ + unicode(self.request.arguments),
            body=body,
            to=profile.email_addresses_list,
            subject='Your account has been activated.')


settings = {
    'debug': configuration.DEBUG,
    #'xsrf_cookies': True,
    'template_path': configuration.TEMPLATE_PATH,
}

urls = (
    (r'/', IndexHandler),
    (r'/profile/?', ProfileHandler),
    (r'/register/?', RegisterHandler),
    (r'/blog/?', BlogHandler),
    (r'/login/?', LoginHandler),
    (r'/logout/?', LogoutHandler),
    (r'/_ah/login_required', LoginHandler),
    (r'/about/?', AboutHandler),
    
    # Api
    (r'/_api/timezones/country/(.*)/?', ApiTimezonesForCountryCodeHandler),
    
    # Workers
    (r'/worker/mail/activate-account/?', WorkerMailActivateAccountHandler),
)

application = WSGIApplication(urls, **settings)

def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == '__main__':
    main()
