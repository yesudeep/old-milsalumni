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
from utils import BaseRequestHandler, SessionRequestHandler, send_mail_once, STATIC_PAGE_CACHE_TIMEOUT
from models import Profile, User
from countries import COUNTRY_ISO_ALPHA_TABLE, COUNTRIES_LIST


####################### Import from version 1 ########################
from models import BLOG_YEAR_LIST, MONTH_LIST,User
######################################################################


try:
    import json
except ImportError:
    from django.utils import simplejson as json


logging.basicConfig(level=logging.DEBUG)

ereporter.register_logger()

class UsersHandler(BaseRequestHandler):
    def get(self):
        
        #getting total, approved and deleted users 
        TOTAL_USER = User.all()
        APPROVED_USER = db.GqlQuery("SELECT * FROM User WHERE is_active=True AND is_deleted = False")
        DELETED_USER = db.GqlQuery("SELECT * FROM User WHERE is_active=False AND is_deleted = True")
        
        self.render('adminusers.html',
                user_count= TOTAL_USER.count(), 
                approved_user_count= APPROVED_USER.count(),
                deleted_user_count= DELETED_USER.count(),
                total_user = TOTAL_USER,
                approved_user = APPROVED_USER,
                deleted_user = DELETED_USER,
                
                page_name='users',
                login_url='/login',
                )

class ArticlesHandler(BaseRequestHandler):
    def get(self):
        self.render('adminusers.html',
                    page_name = 'articles',
                    page_description = 'Add, remove, update articles and publish them.',
                    
                    user_count= User.all().count(),
                    approved_user_count=User.get_approved_user_count(),
                    deleted_user_count=User.get_deleted_user_count(),
                    )

class BooksHandler(BaseRequestHandler):
    def get(self):
        self.render('adminusers.html',
                    page_name = 'books',
                    page_description = 'Add or remove books.',
                    
                    user_count= User.all().count(),
                    approved_user_count=User.get_approved_user_count(),
                    deleted_user_count=User.get_deleted_user_count(),
                    )
                
class AnnouncementsHandler(BaseRequestHandler):
    def get(self):
        self.render('adminusers.html',
                    page_name = 'announcements',
                    page_description = 'Create new announcements to send to everyone in the list of users.',
                    
                    user_count= User.all().count(),                    
                    approved_user_count=User.get_approved_user_count(),
                    deleted_user_count=User.get_deleted_user_count(),
                    )
                
class MailHandler(BaseRequestHandler):
    def get(self):
        self.render('adminusers.html',
                    page_name = 'mails',
                    page_description = 'Send mail to people',
                    
                    approved_user_count=User.get_approved_user_count(),
                    deleted_user_count=User.get_deleted_user_count(),
                    )

class LogoutHandler(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect(users.create_logout_url('/admin'))
        

settings = {
    'debug': configuration.DEBUG,
    #'xsrf_cookies': True,
    'template_path': configuration.TEMPLATE_PATH,
}

urls = (
    (r'/admin/?', UsersHandler),
    (r'/admin/logout/?', LogoutHandler),
    (r'/admin/users/?', UsersHandler),
    (r'/admin/articles/?', ArticlesHandler),
    (r'/admin/books/?', BooksHandler),
    (r'/admin/announcements/?', AnnouncementsHandler),
    (r'/admin/mails/?', MailHandler),
    
)

application = WSGIApplication(urls, **settings)

def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == '__main__':
    main()
