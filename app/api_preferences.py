#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configuration

RPX_REALM = 'mils-alumni-secure'
rpxnow = {
    'api_auth_url': 'https://rpxnow.com/api/v2/auth_info',
    'api_key': 'b771106aa4e3ef377c359495f52f2c99120f36ac',
    'auth_token_url': configuration.ROOT_URL + 'auth_token'
    'realm': RPX_REALM,
    'lang': 'en',
    'domain': '%s.rpxnow.com' % RPX_REALM,
}
