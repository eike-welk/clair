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



class TypeTag(object):
    """Parent for classes that describe the data type of a column or field."""
    def check_type(self, object_):
        raise NotImplementedError

class NoneT(TypeTag):
    """Show that column/field contains a None."""
    def check_type(self, object_):
        return object_ is None
    
class StrT(TypeTag):
    """Show that column/field contains a string."""
    def check_type(self, object_):
        return isinstance(object_, str)

class IntT(TypeTag):
    """Show that column/field contains an integer number."""
    def check_type(self, object_):
        return isinstance(object_, int)

class FloatT(TypeTag):
    """Show that column/field contains a floating point number."""
    def check_type(self, object_):
        return isinstance(object_, float)
    
class ListT(TypeTag):
    """
    Show that column/field contains a list. 
    All values in the list must be of the same type.
    """
    def __init__(self, valueT):
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
    Show that column/field contains a map. 
    All key -> value pairs in the list must be of the same types.
    """
    def __init__(self, keyT, valueT):
        assert isinstance(keyT, TypeTag), "`keyT` must be a `TypeTag`."
        assert isinstance(valueT, TypeTag), "`valueT` must be a `TypeTag`."
        self.keyT = keyT
        self.valueT = valueT
        
    def check_type(self, object_):
        if not isinstance(object_, dict):
            return False
        for k, v in object_.iteritems():
            if not (self.valueT.check_type(v) and self.keyT.check_type(k)):
                return False
        return True


class FieldDescriptor(object):
    """Describe all important aspects of a field or column."""
    def __init__(self, name, data_type, default_val, comment):
        assert isinstance(name, str), "`name` must be a `str`."
        assert isinstance(data_type, TypeTag), \
            "`data_type` must be a `TypeTag`."
        assert check_type(default_val, (data_type, NoneT())), \
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
                "Each element in `field_descriptors` must be a `TypeTag`."
        
        self.name = name
        self.version = version
        self.extension = extension
        self.comment = comment
        self.column_descriptors = field_descriptors
        

def check_type(object_, tags):
    """Equivalent to `isinstance` but with TypeTag"""
    if not isinstance(tags, (list, tuple)):
        tags = (tags,)
        
    is_instance = False
    for tag in tags:
        assert isinstance(tag, TypeTag), \
            "Each element of `tags` must be a `TypeTag`"
        is_instance |= tag.check_type(object_)
    
    return is_instance
