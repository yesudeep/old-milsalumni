#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.api import memcache, urlfetch
from countries import COUNTRY_NAME_ISO_ALPHA_2_TABLE, COUNTRY_NAME_ISO_ALPHA_3_TABLE, ISO_ALPHA_3_CODES


class GeoIP(db.Model):
    ip_address = db.StringProperty()
    country_code = db.StringProperty(choices=ISO_ALPHA_3_CODES)

    @property
    def country_name(self):
        return COUNTRY_NAME_ISO_ALPHA_3_TABLE.get(self.country_code)

    def __unicode__(self):
        return unicode(self.ip_address) + ' => ' + self.country_name
    
    @classmethod
    def country_code_from_ip_address(cls, ip_address):
        """
        Obtains the country code from the given IP address.
        
        http://code.google.com/p/geo-ip-location/wiki/GoogleAppEngine
        """
        cache_key = 'geo_ip_addr_%s' % ip_address
        country_code = memcache.get(cache_key)
    
        if country_code is None:
            geo_ip = GeoIP.all().filter('ip_address = ', ip_address).get()
            if geo_ip:
                country_code = geo_ip.country_code
            else:
                try:
                    response = urlfetch.fetch('http://geoip.wtanaka.com/cc/%s' % ip_address)
                    if response.status_code == 200:
                        country_code = response.content
                except urlfetch.Error, e:
                    pass
            if country_code:
                if not country_code == 'zz':
                    GeoIP(ip_address)
                memcache.set(cache_key, country_code)
        
        return country_code
    
