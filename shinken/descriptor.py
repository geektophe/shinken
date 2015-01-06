#!/usr/bin/env python

# -*- mode: python ; coding: utf-8 -*-

# Copyright (C) 2009-2014:
#     Gabes Jean, naparuba@gmail.com
#     Gerhard Lausser, Gerhard.Lausser@consol.de
#     Gregory Starck, g.starck@gmail.com
#     Hartmut Goebel, h.goebel@goebel-consult.de
#
# This file is part of Shinken.
#
# Shinken is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shinken is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Shinken.  If not, see <http://www.gnu.org/licenses/>.


__all__ = ['PropertyDescriptor']


class PropertyDescriptor(object):

    def __init__(self, name, prop, plus_support=False):
        self.name = name
        self.prop = prop
        self.plus_support = plus_support

    def __get__(self, instance, cls):
        """
        Tries to load the value from a the instance's `__dict__`. If not
        found, tries to load value from the instannce templates by inheritance.
        If still not found, sets property default value.

        :param insance: The instance to get value from
        :param cls:     The instance class
        """
        if self.name in instance.__dict__ and not instance.has_plus(self.name):
            return instance.__dict__[self.name]

        if "templates" not in instance.__dict__:
            raise AttributeError("templates not linkified yet")

        try:
            value = self.get_by_inheritance(instance)

            if value is None:
                value = self.prop.default
        except Exception, e:
            print "(get) try to get by inheratance %s" % (self.name)
            raise

        try:
            if instance.is_tpl() is False:
                print "(get) before pythonize: %s" % value
                value = self.prop.pythonize(value)
                print "(get) after pythonize: %s" % value
        except Exception, e:
            print "(get) tried to pythonize %s: '%s' with %s: %s" % (self.name, value, self.prop.__class__.__name__, e)
            raise

        if not instance.is_tpl() and instance.has_plus(self.name):
            del instance.plus[self.name]
        instance.__dict__[self.name] = value
        return value

    def __set__(self, instance, value):
        """
        Sets the instance attribute using the the property `pythonize()`
        method.

        :param insance: The instance to set value on
        :param cls:     The value to set
        """
        print "Setting: %s.%s = %s" % (instance.__class__.__name__, self.name, value)
        try:
            if instance.is_tpl() is False:
                print "(set) before pythonize: %s" % value
                value = self.prop.pythonize(value)
                print "(set) after pythonize: %s" % value
        except Exception, e:
            print "(set) tried to pythonize %s: '%s' with %s" % (self.name, value, self.prop.__class__.__name__, e)
            raise
        #value = self.prop.pythonize(value)
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        """
        Deletes the instance attribute.

        :param insance: The instance to delete value from
        """
        if self.name in instance.__dict__:
            del instance[self.name]

    def get_by_inheritance(self, item):
        """
        Looks for a property in item's templates.
        """
        values = []

        if self.name in item.__dict__:
            value = item.__dict__[self.name]
            if self.plus_support is False or item.is_plus() is False:
                return value
            else:
                values.append(value)

        for i in item.templates:
            value = self.get_by_inheritance(i)
            if value is not None:
                values.append(value)
            if self.plus_support is False or i.has_plus(self.name) is False:
                break

        try:
            if values:
                return ",".join(values)
            else:
                return None
        except:
            print "tried to split: %s" % values
            raise
