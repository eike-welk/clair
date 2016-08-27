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
Definitions of the the ``pandas.DataFrame`` objects that store the 
application's important data in 2D tables.
"""

from __future__ import division
from __future__ import absolute_import              

from numpy import nan, isnan #IGNORE:E0611
import numpy as np
import pandas as pd

from clair.descriptors import BoolT, IntT, FloatT, \
                              FieldDescriptor, TableDescriptor

from clair.coredata import LISTING_DESCRIPTOR, PRICE_DESCRIPTOR



def make_data_series(descriptor, nrows=None, index=None):
    """
    Create an empty ``pandas.Series``  as specified by ``descriptor``. 
    """
    assert isinstance(descriptor, FieldDescriptor)
    assert nrows is not None or index is not None, \
           "Either ``nrows`` or ``index`` must be specified."
    
    if index is None:
        index=range(nrows)
    if nrows is not None:
        assert nrows == len(index), "Inconsistent arguments"
    
    if   descriptor.data_type == BoolT:
        dtype = object
    elif descriptor.data_type == IntT:
        dtype = float
    elif descriptor.data_type == FloatT:
        dtype = float
    else:
        dtype = object

    default_val = descriptor.default_val
        
    return pd.Series(data=default_val, index=index, dtype=dtype)
    
    
def make_data_frame(descriptor, nrows=None, index=None):
    """
    Create an empty ``pandas.DataFrame`` as specified by ``descriptor``. 
    
    Column labels, data types, and default values are taken from ``descriptor``.
    The object contains no data, all values are ``nan`` or the column's 
    default values.
    
    Arguments ``nrows`` and ``index`` both are optional, 
    but one of them must be given. 
    If both arguments are given they must be consistent.
    
    Arguments
    ---------
    
    descriptor : TableDescriptor
        Contains column labels, data types, and default values.
        
    nrows : int 
        Number of rows.
        
    index : iterable 
        The index labels of the new data frame. 
        If this argument is omitted or ``None``, a sequence of integers 
        (``range(nrows)``) is used as index labels.
    """
    assert isinstance(descriptor, TableDescriptor)
    assert nrows is not None or index is not None, \
           "Either ``nrows`` or ``index`` must be specified."
           
    if index is None:
        index=range(nrows)
    if nrows is not None:
        assert nrows == len(index), "Inconsistent arguments"
    
    dframe = pd.DataFrame(index=index)
    for fieldD in descriptor.column_descriptors:
        col = make_data_series(fieldD, index=index)
        dframe[fieldD.name] = col
        
    return dframe


def make_listing_frame(nrows=None, index=None):
    """
    Create empty ``pd.DataFrame`` of listings. 
    
    Each row represents a listing. The columns represent the listing's 
    attributes. The object contains no data, all values are ``None`` or ``nan``.

    Arguments
    ---------
    nrows : int 
        Number of listings/auctions. 
    index : iterable 
        The index labels of the new data frame. 
        If this argument is omitted or ``None``, a sequence of integers 
        (``range(nrows)``) is used as index labels.
    """
    return make_data_frame(LISTING_DESCRIPTOR, nrows, index)


def make_listing_id(listing):
    """
    Create unique ID string for a listing.
    """
    return unicode(listing["site"] + "-" + listing["date"] + "-" + 
                   listing["site_id"])


def make_price_frame(nrows=None, index=None):
    """
    Create empty ``pd.DataFrame`` of prices. 
    
    Each row represents a price. The columns represent the price's 
    attributes. The object contains no data, all values are ``None`` or ``nan``.

    Arguments
    ---------
    nrows : int 
        Number of listings/auctions. 
    index : iterable 
        The index labels of the new data frame. 
        If this argument is omitted or ``None``, a sequence of integers 
        (``range(nrows)``) is used as index labels.
    """
    return make_data_frame(PRICE_DESCRIPTOR, nrows, index)


def make_price_id(price):
    """
    Create unique ID string for a price.
    """    
    return unicode(price["time"] + "-" + price["product"] + "-"  + 
                   price["type"] + "-" + price["listing"])
