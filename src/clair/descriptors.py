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
Tools to define the structure of DataFrame objects, JSON-Files, XML-Files, and 
databases.  
"""

from datetime import datetime



class TypeDescriptor(object):
    """Parent for classes that describe the data type of a column or field."""
    def is_py_instance(self, object_):
        raise NotImplementedError

class SimpleTypeDescriptor(TypeDescriptor):
    """A tag that describes a simple type like `int` or `float`."""
    def __init__(self, pythonType):
        TypeDescriptor.__init__(self)
        assert isinstance(pythonType, type), \
            "`pythonType` must be a Python type. For example `int` or `str`."
        self.pythonType = pythonType
        
    def is_py_instance(self, object_):
        return isinstance(object_, self.pythonType)


NoneD = SimpleTypeDescriptor(type(None))
StrD = SimpleTypeDescriptor(str)
BoolD = SimpleTypeDescriptor(bool)
IntD = SimpleTypeDescriptor(int)
FloatD = SimpleTypeDescriptor(float)
DateTimeD = SimpleTypeDescriptor(datetime)


class SumTypeD(TypeDescriptor):
    """
    Sum type or union type. The object can be an instance of one of several types.
    """
    def __init__(self, *tags):
        TypeDescriptor.__init__(self)
        for tag in tags:
            assert isinstance(tag, TypeDescriptor), \
                "Each argument of the constructor must be a `FieldDescriptor`."
        self.tags = tags
    
    def is_py_instance(self, object_):
        for tag in self.tags:
            if tag.is_py_instance(object_):
                return True
        return False


class ListD(TypeDescriptor):
    """
    Show that column/field contains a list. 
    All values in the list must be of the same type.
    """
    def __init__(self, valueT):
        TypeDescriptor.__init__(self)
        assert isinstance(valueT, TypeDescriptor), "`valueT` must be a `TypeDescriptor`."
        self.valueT = valueT
    
    def is_py_instance(self, object_):
        if not isinstance(object_, list):
            return False
        for v in object_:
            if not self.valueT.is_py_instance(v):
                return False
        return True
            
            
class DictD(TypeDescriptor):
    """
    Show that column/field contains a `dict`. 
    All key -> value pairs in the list must be of the same types.
    """
    def __init__(self, keyT, valueT):
        TypeDescriptor.__init__(self)
        assert isinstance(keyT, TypeDescriptor), "`keyT` must be a `TypeDescriptor`."
        assert isinstance(valueT, TypeDescriptor), "`valueT` must be a `TypeDescriptor`."
        self.keyT = keyT
        self.valueT = valueT
        
    def is_py_instance(self, object_):
        if not isinstance(object_, dict):
            return False
        for k, v in object_.items():
            if not (self.keyT.is_py_instance(k) and self.valueT.is_py_instance(v)):
                return False
        return True


def is_py_instance(object_, tag):
    """Equivalent to `isinstance` but with TypeDescriptor"""
    assert isinstance(tag, TypeDescriptor), "`tag` must be a `TypeDescriptor`."
    return tag.is_py_instance(object_)
         

class FieldDescriptor(object):
    """Describe all important aspects of a field or column."""
    def __init__(self, name, data_type, default_val, comment):
        assert isinstance(name, str), "`name` must be a `str`."
        assert isinstance(data_type, TypeDescriptor), \
            "`data_type` must be a `TypeDescriptor`."
        assert is_py_instance(default_val, SumTypeD(data_type, NoneD)), \
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
