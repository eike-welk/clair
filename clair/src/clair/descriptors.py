# -*- coding: utf-8 -*-
###############################################################################
#    Clair - Project to discover prices on e-commerce sites.                  #
#                                                                             #
#    Copyright (C) 2016 by Eike Welk                                          #
#    eike.welk@gmx.net                                                        #
#                                                                             #
#    License: GPL Version 3                                                   #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
###############################################################################
"""
Tools to define the structure of DataFrame objects, XML-Files, and databases.  
"""

from __future__ import division
from __future__ import absolute_import              

from types import NoneType, TypeType



class TypeTag(object):
    """Parent for classes that describe the data type of a column or field."""
    def check_type(self, object_):
        raise NotImplementedError

class SimpleTypeMetaT(TypeTag):
    """A tag that describes a simple type like `int` or `float`."""
    def __init__(self, pythonType):
        TypeTag.__init__(self)
        assert isinstance(pythonType, TypeType), \
            "`pythonType` must be a Python type. For example `int` or `str`."
        self.pythonType = pythonType
        
    def check_type(self, object_):
        return isinstance(object_, self.pythonType)

NoneT = SimpleTypeMetaT(NoneType)
StrT = SimpleTypeMetaT(str)
IntT = SimpleTypeMetaT(int)
FloatT = SimpleTypeMetaT(float)

class SumT(TypeTag):
    """
    Sum type or union. The object can be an instance of one of several types.
    """
    def __init__(self, *tags):
        TypeTag.__init__(self)
        for tag in tags:
            assert isinstance(tag, TypeTag)
        self.tags = tags
    
    def check_type(self, object_):
        for tag in self.tags:
            if tag.check_type(object_):
                return True
        return False

class ListT(TypeTag):
    """
    Show that column/field contains a list. 
    All values in the list must be of the same type.
    """
    def __init__(self, valueT):
        TypeTag.__init__(self)
        assert isinstance(valueT, TypeTag), "`valueT` must be a `TypeTag`."
        self.valueT = valueT
    
    def check_type(self, object_):
        if not isinstance(object_, list):
            return False
        for v in object_:
            if not self.valueT.check_type(v):
                return False
        return True
            
class DictT(TypeTag):
    """
    Show that column/field contains a `dict`. 
    All key -> value pairs in the list must be of the same types.
    """
    def __init__(self, keyT, valueT):
        TypeTag.__init__(self)
        assert isinstance(keyT, TypeTag), "`keyT` must be a `TypeTag`."
        assert isinstance(valueT, TypeTag), "`valueT` must be a `TypeTag`."
        self.keyT = keyT
        self.valueT = valueT
        
    def check_type(self, object_):
        if not isinstance(object_, dict):
            return False
        for k, v in object_.iteritems():
            if not (self.keyT.check_type(k) and self.valueT.check_type(v)):
                return False
        return True

def check_type(object_, tag):
    """Equivalent to `isinstance` but with TypeTag"""
    assert isinstance(tag, TypeTag), "`tag` must be a `TypeTag`."
    return tag.check_type(object_)
         

class FieldDescriptor(object):
    """Describe all important aspects of a field or column."""
    def __init__(self, name, data_type, default_val, comment):
        assert isinstance(name, str), "`name` must be a `str`."
        assert isinstance(data_type, TypeTag), \
            "`data_type` must be a `TypeTag`."
        assert check_type(default_val, SumT(data_type, NoneT)), \
            "`default_val` must be of the type described by `data_type` or None"
        assert isinstance(comment, str), "`comment` must be a `str`."
        
        self.name = name
        self.data_type = data_type
        self.default_val = default_val
        self.comment = comment

class TableDescriptor(object):
    """
    Describe all important aspects of a table or database.
    """
    def __init__(self, name, version, extension, comment, field_descriptors):
        assert isinstance(name, str), "`name` must be a `str`."
        assert isinstance(version, str), "`version` must be a `str`."
        assert isinstance(extension, str), "`extension` must be a `str`."
        assert isinstance(comment, str), "`comment` must be a `str`."
        assert isinstance(field_descriptors, list), \
            "`field_descriptors` must be a `list`."
        for descr in field_descriptors:
            assert isinstance(descr, FieldDescriptor), \
                "Each element in `field_descriptors` must be a `FieldDescriptor`."
        
        self.name = name
        self.version = version
        self.extension = extension
        self.comment = comment
        self.column_descriptors = field_descriptors
