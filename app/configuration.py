#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Application configuration.
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

# Some boilerplate.
import sys
import os

from os.path import dirname, abspath, realpath, join as path_join

DIR_PATH = abspath(dirname(realpath(__file__)))
#LIB_PATH = path_join(DIR_PATH, 'lib')
LIB_PATH = DIR_PATH
EXTRA_LIB_PATH = [
    dirname(DIR_PATH),
    LIB_PATH,
    path_join(LIB_PATH, 'tornado'),
    path_join(LIB_PATH, 'appengine_gaefy'),
    path_join(LIB_PATH, 'aeoid'),
    path_join(LIB_PATH, 'gaeutilities'),
]
sys.path = EXTRA_LIB_PATH + sys.path
# End boilerplate.

# Place your imports here.

def sanitize_url(url):
    """Ensures that the URL ends with a slash."""
    if not url.endswith('/'):
        url = url + '/'
    return url

NAKED_DOMAIN = 'milsalumni.org'
SUBDOMAIN = 'www'
ADMIN_EMAIL = "administrator@%s" % (NAKED_DOMAIN, )
SUPPORT_EMAIL = 'team@%s' % (NAKED_DOMAIN, )
NOREPLY_EMAIL = 'noreply@%s' % (NAKED_DOMAIN, )
CONTACT_EMAIL = SUPPORT_EMAIL
APPLICATION_ID = os.environ['APPLICATION_ID']
APPLICATION_TITLE = "MILS Alumni"
MODE_DEVELOPMENT = 'development'
MODE_PRODUCTION = 'production'
SERVER_PORT = os.environ['SERVER_PORT']
SERVER_NAME = os.environ['SERVER_NAME']
SERVER_SOFTWARE = os.environ['SERVER_SOFTWARE']
APPSPOT_DOMAIN = "%s.appspot.com" % APPLICATION_ID

DEVELOPER_URL = "http://happychickoo.com"
DEVELOPER_NAME = "happychickoo"

MAIL_SUBJECT_PREFIX = "[MILS Alumni] "
MAIL_SIGNATURE = """--
For more information please visit http://www.%s""" % NAKED_DOMAIN

# Analytics identifiers.
GOOGLE_ANALYTICS_ID = 'UA-7340598-3'

OWNER_NAME = 'MILS Alumni'
OWNER_ADDRESS = ''
OWNER_URL = 'http://www.%s' % NAKED_DOMAIN
OWNER_COMPANY = 'MILS Alumni'
COPYRIGHT_YEARS = '2009, 2010'

TEXT_MEDIA_URL = '/s/'
MEDIA_URL = TEXT_MEDIA_URL

if SERVER_PORT and SERVER_PORT != '80':
    # We are using the development server.
    DEPLOYMENT_MODE = MODE_DEVELOPMENT
    HOST_NAME = '%s:%s' % (SERVER_NAME, SERVER_PORT,)
    LOCAL = True
    DEBUG = True
    #MEDIA_URL = 'http://%s/s/' % (HOST_NAME, )
else:
    # We are using the production server.
    DEPLOYMENT_MODE = MODE_PRODUCTION
    HOST_NAME = SERVER_NAME
    LOCAL = False
    DEBUG = False
    MEDIA_URL = "http://%s/s/" % (APPSPOT_DOMAIN,)
    TEXT_MEDIA_URL = MEDIA_URL
    #TEXT_MEDIA_URL = "http://assets.%s/" % (NAKED_DOMAIN, )


if DEBUG:
    # Minification suffixes to use for CSS and JS files.
    CSS_MINIFIED = ''
    JS_MINIFIED = ''
else:
    CSS_MINIFIED = '-min'
    JS_MINIFIED = '-min'


# The URL root of the Website.
# For example:
#     http://www.example.com/
#     http://localhost:8000/
ROOT_URL = 'http://%s/' % (HOST_NAME,)


# ---------------------------------------------------------------------------
# Stuff that should be different in production.
cdn_urls = {
    'microsoft.jquery-1.3.2': "http://ajax.microsoft.com/ajax/jQuery/jquery-1.3.2.min.js",
    'google.jquery-1.3.2': "http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js",
    'google.jquery-1.4': 'http://ajax.googleapis.com/ajax/libs/jquery/1.4.1/jquery.min.js',
    'jquery.jquery-1.4': "http://code.jquery.com/jquery-1.4.min.js",
    'local.jquery-1.4': "%sscript/lib/chickoojs/src/jquery/jquery-1.4.min.js" % (MEDIA_URL,),
    'local.jquery-1.3.2': "%sscript/lib/chickoojs/src/jquery/jquery-1.3.2.min.js" % (MEDIA_URL,),
}

if LOCAL:
    JQUERY_URL = cdn_urls.get('local.jquery-1.4')
    ANALYTICS_CODE = ""
else:
    JQUERY_URL = cdn_urls.get('google.jquery-1.4')
    ANALYTICS_CODE = """<script type="text/javascript">var _gaq=_gaq||[];_gaq.push(['_setAccount', '%(GOOGLE_ANALYTICS_ID)s']);
_gaq.push(['_trackPageview']);(function(){var doc=document,ga=doc.createElement('script');
ga.src=('https:'==doc.location.protocol?'https://ssl':'http://www')+'.google-analytics.com/ga.js';
ga.setAttribute('async', 'true');doc.documentElement.firstChild.appendChild(ga);})();</script>
""" % dict(GOOGLE_ANALYTICS_ID=GOOGLE_ANALYTICS_ID)


# The builtin variables that are available to all templates.
TEMPLATE_BUILTINS = {
    'ADMIN_EMAIL': ADMIN_EMAIL,
    'ANALYTICS_CODE': ANALYTICS_CODE,
    'APPLICATION_NAME': APPLICATION_TITLE,
    'APPLICATION_TITLE': APPLICATION_TITLE,
    'CONTACT_EMAIL': CONTACT_EMAIL,
    'COPYRIGHT_YEARS': COPYRIGHT_YEARS,
    'CSS_MINIFIED': CSS_MINIFIED,
    'DEBUG': DEBUG,
    'DEPLOYMENT_MODE': DEPLOYMENT_MODE,
    'DEVELOPER_NAME': DEVELOPER_NAME,
    'DEVELOPER_URL': DEVELOPER_URL,
    'GOOGLE_ANALYTICS_ID': GOOGLE_ANALYTICS_ID,
    'JQUERY_URL': JQUERY_URL,
    'JS_MINIFIED': JS_MINIFIED,
    'LOCAL': LOCAL,
    'MAIL_SIGNATURE': MAIL_SIGNATURE,
    'MEDIA_URL': sanitize_url(MEDIA_URL),
    'NAKED_DOMAIN': NAKED_DOMAIN,
    'OWNER_ADDRESS': OWNER_ADDRESS,
    'OWNER_COMPANY': OWNER_COMPANY,
    'OWNER_NAME': OWNER_NAME,
    'OWNER_URL': OWNER_URL,
    'ROOT_URL': sanitize_url(ROOT_URL),
    'TEMPLATE_DEBUG': DEBUG,
    'TEXT_MEDIA_URL': TEXT_MEDIA_URL,
}


TEMPLATE_PATH = path_join(DIR_PATH, 'templates')
