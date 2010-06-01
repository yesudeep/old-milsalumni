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

from google.appengine.api import users
from google.appengine.ext import db, ereporter
from google.appengine.ext.webapp.util import run_wsgi_app, login_required
from tornado.wsgi import WSGIApplication
from utils import BaseRequestHandler, SessionRequestHandler, send_mail_once

logging.basicConfig(level=logging.DEBUG)

ereporter.register_logger()

class IndexHandler(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect('/profile')
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
        from models import Profile

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
        user = users.get_current_user()
        if user:
            logging.info("Federated identity: " + str(user.federated_identity()))
        else:
            logging.info("NO USER?")
        
        return
        
        self.render('register.html', logout_url=users.create_logout_url('/'))


class ProfileHandler(BaseRequestHandler):
    @login_required
    def get(self):
        self.render('profile.html', logout_url=users.create_logout_url('/'))


class AboutHandler(BaseRequestHandler):
    @login_required
    def get(self):
        self.render('about.html', logout_url=users.create_logout_url('/'))


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
