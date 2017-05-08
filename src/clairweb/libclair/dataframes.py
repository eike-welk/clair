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
Functions that create ``pandas.DataFrame`` objects.

A ``DataFrame`` is a 2-dimensional table.  Each column has a *name* and each row
has an *index*. The elements of a column all have the same data type. A row can
contain elements of diffentent types.

A ``DataFrame`` can repesent a table from the database in the comuter's RAM.
Algorithms that involve multiple rows of a table are implemented with
``DataFrame`` objects.
"""

import numpy as np
import pandas  as pd
from django.db import models

from libclair import descriptors 



def convert_model_to_descriptor(dj_model):
    """
    Convert a Django database model into an equivalent Clair descriptor.
    """
    assert issubclass(dj_model, models.Model)
    
    dj_fields = dj_model._meta.get_fields()
    fields = [_convert_field_to_descriptor(f) for f in dj_fields
              if f.auto_created == False]

    return descriptors.TableDescriptor(dj_model.__name__, 
                                       '0', 
                                       dj_model.__name__ + '.json', 
                                       dj_model.__doc__ if dj_model.__doc__ is not None else '', 
                                       fields)

def _convert_field_to_descriptor(dj_field):
    """
    Convert a Django database dj_field to an equivalent Clair descriptor.
    """
    assert isinstance(dj_field, models.Field)
    
    type_trans = {
        models.CharField: descriptors.StrD,
        models.FloatField: descriptors.FloatD,
        models.IntegerField: descriptors.IntD,
        models.BooleanField: descriptors.BoolD,
        models.NullBooleanField: descriptors.BoolD,
        models.DateField: descriptors.DateTimeD,
        models.DateTimeField: descriptors.DateTimeD,
        }
    
    cl_type = type_trans[type(dj_field)]
    return descriptors.FieldDescriptor(str(dj_field.name), 
                                       cl_type, 
                                       dj_field.get_default(), 
                                       dj_field.verbose_name)


def make_data_series(descr, nrows=None, index=None):
    """
    Create an empty ``pandas.Series``. 
    
    Parameters
    ----------
    
    descr: ``descriptors.FieldDescriptor``, ``models.Field``
        Description of data type and default value
        of the stored data.
        
    nrows: ``int``
        Number of elements in the new ``pandas.Series`` object.
        
    index: ``list``, ``pandas.Index``
        The index of the new series. Basically a list of primary keys.

        If this argument is omitted or ``None``, a sequence of integers 
        (``range(nrows)``) is used as index labels.
    """
    assert isinstance(descr, (descriptors.FieldDescriptor, models.Field))
    assert nrows is not None or index is not None, \
           "Either ``nrows`` or ``index`` must be specified."

    if isinstance(descr, models.Field):
        descr = _convert_field_to_descriptor(descr)
    
    #Create the index if it is not given.
    if index is None:
        index=list(range(nrows))
    if nrows is not None:
        assert nrows == len(index), "Inconsistent arguments"

    default_val = descr.default_val
    
    if descr.data_type == descriptors.DateTimeD:
        temp = pd.Series(data=default_val, index=index, dtype=pd.Timestamp)
        return pd.to_datetime(temp)
        
    if   descr.data_type == descriptors.BoolD:
        dtype = object
    elif descr.data_type == descriptors.IntD:
        dtype = np.int32
    elif descr.data_type == descriptors.FloatD:
        dtype = np.float64
    else:
        dtype = object
    return pd.Series(data=default_val, index=index, dtype=dtype)


def make_data_frame(descr, nrows=None, index=None):
    """
    Create an empty ``pandas.DataFrame`` as specified by ``descr``. 
    
    Column labels, data types, and default values are taken from ``descr``.
    The object contains no data, all values are ``nan`` or the column's 
    default values.
    
    Arguments ``nrows`` and ``index`` both are optional, 
    but one of them must be given. 
    If both arguments are given they must be consistent.
    
    Arguments
    ---------
    
    descr : TableDescriptor
        Contains column labels, data types, and default values.
        
    nrows : int 
        Number of rows.
        
    index : iterable 
        The index labels (primary keys) of the new data frame. 
        
        If this argument is omitted or ``None``, a sequence of integers 
        (``range(nrows)``) is used as index labels.
    """
    assert isinstance(descr, descriptors.TableDescriptor) or \
           issubclass(descr, models.Model)
    assert nrows is not None or index is not None, \
           "Either ``nrows`` or ``index`` must be specified."
    
    if isinstance(descr, type) and issubclass(descr, models.Model):
        descr = convert_model_to_descriptor(descr)
           
    if index is None:
        index=list(range(nrows))
    if nrows is not None:
        assert nrows == len(index), "Inconsistent arguments"
    
    dframe = pd.DataFrame(index=index)
    for fieldD in descr.column_descriptors:
        col = make_data_series(fieldD, index=index)
        dframe[fieldD.name] = col
        
    return dframe


def make_price_id(price):
    """
    Create unique ID string for a price.
    """    
    return (str(price["time"]) + "-" + price["product"] + "-"  + 
            price["type"] + "-" + price["listing"])
