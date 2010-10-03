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
        username = user.nickname()
        
        cache_key = 'admin page' + username
        cached_response = memcache.get(cache_key)
        if cached_response:
            self.write('cached response')
        else:
            if '@' in username:
                username = username[:username.find('@')]
            self.render('adminindex.html', 
                video_url=configuration.INTRO_VIDEO_URL, 
                login_url='/login')

settings = {
    'debug': configuration.DEBUG,
    #'xsrf_cookies': True,
    'template_path': configuration.TEMPLATE_PATH,
}

urls = (
    (r'/admin', IndexHandler),
)

application = WSGIApplication(urls, **settings)

def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == '__main__':
    main()
