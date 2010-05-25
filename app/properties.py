#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from base64 import b64encode, b64decode
import decimal

class DecimalProperty(db.Property):
    """
    Stores decimal.Decimal values.
    """
    data_type = decimal.Decimal

    def get_value_for_datastore(self, model_instance):
        return str(super(DecimalProperty, self).get_value_for_datastore(model_instance))

    def make_value_from_datastore(self, value):
        return decimal.Decimal(value)

    def validate(self, value):
        value = super(DecimalProperty, self).validate(value)

        if value is None or isinstance(value, decimal.Decimal):
            return value
        elif isinstance(value, basestring):
            return decimal.Decimal(value)
        raise db.BadValueError("Property %s must be a Decimal or string" % self.name)


class Base64Property(db.StringProperty):
    """
    Stores strings in the base64 encoded format.
    Automatically decodes when reading the value.
    """
    def __init__(self, verbose_name=None, **kwds):
        super(Base64Property, self).__init__(verbose_name, multiline=False, **kwds)

    def get_value_for_datastore(self, model_instance):
        value = self.__get__(model_instance, model_instance.__class__)
        if value is not None:
            return b64encode(value)

    def make_value_from_datastore(self, value):
        if value is not None:
            return b64decode(value)
