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
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app, login_required
from tornado.wsgi import WSGIApplication
from utils import BaseRequestHandler, SessionRequestHandler, send_mail_once

logging.basicConfig(level=logging.DEBUG)


class IndexHandler(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect('/blog')
        else:
            self.render('index.html', login_url='/login')


class LoginHandler(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect('/blog')
        else:
            self.render('login.html')
        
    def post(self):
        federated_identity = self.get_argument('openid_identifier')
        logging.info(federated_identity)
        login_url = users.create_login_url(dest_url='/blog', federated_identity=federated_identity)
        self.redirect(login_url)


class BlogHandler(BaseRequestHandler):
    @login_required
    def get(self):
        self.render('blog.html', logout_url=users.create_logout_url('/'))


class AboutHandler(BaseRequestHandler):
    @login_required
    def get(self):
        self.render('about.html', logout_url=users.create_logout_url('/'))


class AuthenticationTokenHandler(SessionRequestHandler):
    """
    Handle authentication token request sent by RPXNOW.
    """
    def convert_to_auth_profile(self, rpx_profile):
        pass 
    
    def get(self):
        from urllib import urlencode
        from google.appengine.api import urlfetch
        from api_preferences import rpxnow
        try:
            import json
        except ImportError:
            from django.utils import simplejson as json

        token = self.get_argument('token')
        arguments = {
            'format': 'json',
            'apiKey': rpxnow.get('api_key'),
            'token': token,
        }
        api_response = urlfetch.fetch(
            url=rpxnow.get('api_auth_url'),
            payload=urlencode(arguments),
            method=urlfetch.POST,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            })
        response_content = json.loads(api_response.content)
        logging.info('@AuthenticationTokenHandler: %s' % (api_response.content,))
        
        if response_content['stat'] == 'ok':
            auth_profile = self.convert_to_auth_profile(response_content['profile'])
        else:
            self.redirect('/')


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
    (r'/blog/?', BlogHandler),
    (r'/login/?', LoginHandler),
    (r'/about/?', AboutHandler),
    (r'/auth_token/?', AuthenticationTokenHandler),
    
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
