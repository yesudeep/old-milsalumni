#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.api import memcache, urlfetch


def country_code_from_ip_address(ip_address):
    """
    Obtains the country code from the given IP address.

    http://code.google.com/p/geo-ip-location/wiki/GoogleAppEngine
    """
    cache_key = 'geo_ip_addr_%s' % ip_address
    country_code = memcache.get(cache_key)

    if country_code is None:
        try:
            response = urlfetch.fetch('http://geoip.wtanaka.com/cc/%s' % ip_address)
            if response.status_code == 200:
                country_code = response.content
        except urlfetch.Error, e:
            pass
        if country_code:
            memcache.set(cache_key, country_code)

    return country_code
