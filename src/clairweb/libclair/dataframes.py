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
Functions that create the ``pandas.DataFrame`` objects that store the 
application's important data in 2D tables.
"""

import numpy as np
import pandas  as pd
from django.db import models

from libclair import descriptors 


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
    """
    assert isinstance(descr, (descriptors.FieldDescriptor, models.Field))
    assert nrows is not None or index is not None, \
           "Either ``nrows`` or ``index`` must be specified."
    
    #Create the index if it is not given.
    if index is None:
        index=list(range(nrows))
    if nrows is not None:
        assert nrows == len(index), "Inconsistent arguments"

    if isinstance(descr, descriptors.FieldDescriptor):
        return _make_data_series_from_descriptor(descr, index)
    elif isinstance(descr, models.Field):
        return _make_data_series_from_model(descr, index)
    else:
        raise TypeError(
            "Unknown data type description for creation of ``pandas.series``.")

def _make_data_series_from_descriptor(descr, index=None):
    """
    Create an empty ``pandas.Series``. 
    The data type is specified by a ``libclair.descriptors.FieldDescriptor``.
    """
    assert isinstance(descr, descriptors.FieldDescriptor)

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

def _make_data_series_from_model(descr, index=None):
    """
    Create an empty ``pandas.Series``. 
    The data type is specified by a ``django.db.models.Field``.
    """
    assert isinstance(descr, models.Field)

    default_val = descr.get_default()
    
    if isinstance(descr, (models.DateField, models.DateTimeField)):
        temp = pd.Series(data=default_val, index=index, dtype=pd.Timestamp)
        return pd.to_datetime(temp)
        
    if   isinstance(descr, models.IntegerField):
        dtype = np.int32
    elif isinstance(descr, models.FloatField):
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
        The index labels of the new data frame. 
        If this argument is omitted or ``None``, a sequence of integers 
        (``range(nrows)``) is used as index labels.
    """
    assert isinstance(descr, descriptors.TableDescriptor)
    assert nrows is not None or index is not None, \
           "Either ``nrows`` or ``index`` must be specified."
           
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
