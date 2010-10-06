#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Utilities.
# Copyright (c) 2010 happychickoo.
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

from google.appengine.api import memcache, mail
from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp

import re
import tornado.web
import tornado.wsgi
import unicodedata
import hashlib
import logging
from base64 import b64encode, b64decode
from uuid import uuid1


from datetime import datetime
from functools import partial
from urllib import urlencode


logging.basicConfig(level=logging.DEBUG)

EMAIL_SENDER = configuration.NOREPLY_EMAIL
EMAIL_REPLY_TO = configuration.SUPPORT_EMAIL

STATIC_PAGE_CACHE_TIMEOUT = 15   # half an hour.

# Conveninence wrapper to make sure int conversion uses a decimal base.
dec = partial(int, base=10)


def queue_task(queue_name='default', *args, **kwargs):
    """
    Queues a task for execution asynchronously.
    """
    taskqueue.Task(*args, **kwargs).add(queue_name)
    info = ' %(url)s %(method)s' % kwargs
    logging.info('[%s]' % (queue_name,) + info)


def queue_mail_task(*args, **kwargs):
    """
    The queue mail-queue must be defined in the queue.yaml file.
    """
    queue_task('mail-queue', *args, **kwargs)


def send_mail_once(cache_key, worker_url, body, to, subject, reply_to=EMAIL_REPLY_TO, sender=EMAIL_SENDER, **kwargs):
    """
    Will send email only once.  This uses memcache-based lock to avoid sending email
    more than once.  However, since memcached is distributed and may not be permanently
    available, stray duplicates may be found.
    """

    if kwargs.has_key("bcc"):
        additional_key_params = """bcc: \"%s\",""" % (kwargs.get("bcc"),)
    else:
        additional_key_params = ""
    cache_key = """
        {
            worker_url: \"%s\",
            cache_key: \"%s\",
            subject: \"%s\",
            sent_to: \"%s\",
            sent_by: \"%s\",
            reply_to: \"%s\",
            %s
            body: \"%s\",
        }
    """ % (worker_url, cache_key, subject, to, sender, reply_to, additional_key_params, body)

    logging.info('Attempting to send mail: \n' + cache_key)

    if not memcache.get(cache_key):
        mail.send_mail(sender=sender,
            to=to,
            reply_to=reply_to,
            subject=subject,
            body=body,
            **kwargs)
        logging.info("Mail Worker: " + cache_key)
        memcache.set(cache_key, True, 120)
        logging.info('Sent mail.')
    else:
        logging.info('Mail sent before.  Not sending again.')


def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    return re.sub('[^a-zA-Z0-9-]+', '-', s).strip('-')


def datetimeformat(value, format="%Y-%m-%dT%H:%M:%SZ"):
    if value and hasattr(value, 'strftime'):
        formatted_datetime = value.strftime(format)
    else:
        formatted_datetime = ""
    return formatted_datetime


def truncate(s, length=255, killwords=False, end='...'):
    """Return a truncated copy of the string. The length is specified
    with the first parameter which defaults to ``255``. If the second
    parameter is ``true`` the filter will cut the text at length. Otherwise
    it will try to save the last word. If the text was in fact
    truncated it will append an ellipsis sign (``"..."``). If you want a
    different ellipsis sign than ``"..."`` you can specify it using the
    third parameter.

    .. sourcecode jinja::

        {{ mytext|truncate(300, false, '&raquo;') }}
            truncate mytext to 300 chars, don't split up words, use a
            right pointing double arrow as ellipsis sign.
    """
    if len(s) <= length:
        return s
    elif killwords:
        return s[:length] + end
    words = s.split(' ')
    result = []
    m = 0
    for word in words:
        m += len(word) + 1
        if m > length:
            break
        result.append(word)
    result.append(end)
    return u' '.join(result)


def get_previous_month(d=None):
    """
    Given a datetime value, determines the previous month.
    """
    if not d:
        d = datetime.utcnow()
    months = range(0, 12)
    month_index = d.month - 1
    previous_m_index = month_index - 1
    if previous_m_index < 0:
        year = d.year - 1
    else:
        year = d.year
    return datetime(year, months[previous_m_index] + 1, 1)


def hash_password(password_string, salt=None):
    """
    Hashes a password with a unique salt and returns the
    hexdigest and the salt as a tuple (powered 2).
    """
    hash_function = hashlib.sha1()
    if not salt:
        random_salt = str(uuid1())
    else:
        random_salt = salt
    hash_function.update(random_salt + password_string)
    hexdigest = hash_function.hexdigest()
    if not salt:
        return (hexdigest, random_salt)
    else:
        return hexdigest


class BaseRequestHandler(tornado.web.RequestHandler):
    def render_string(self, template_name, **values):
        template_values = {}
        template_values.update(configuration.TEMPLATE_BUILTINS)
        template_values.update(values)
        return tornado.web.RequestHandler.render_string(self, template_name, **template_values)


class SessionRequestHandler(BaseRequestHandler):
    def __init__(self, application, request, transforms=None):
        super(SessionRequestHandler, self).__init__(application, request, transforms)
        from appengine_utilities import sessions
        self.session = sessions.Session()

    def get_current_username(self):
        return self.session.get('username')

    def is_logged_in(self):
        return self.session.get('is_logged_in', False)

    def do_login(self, username):
        logging.info('>> logging in user %s' % username)
        self.session['is_logged_in'] = True
        self.session['username'] = username

    def do_logout(self):
        self.session['is_logged_in'] = False
        #del self.session['username']
