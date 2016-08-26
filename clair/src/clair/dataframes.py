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

from clair.descriptors import (
                    NoneT, BoolT, StrT, IntT, FloatT, SumT, ListT, DictT,
                    FieldDescriptor, TableDescriptor)
FD = FieldDescriptor



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



#
#listingsDescriptor = TableDescriptor(
#    "listings_frame", "1.0", "dframe", 
#    "2D Table of dframe. "
#    "Each row represents a listing on an e-commerce site.", 
#    [FD("id", StrT, None, 
#        "Internal unique ID of each listing."),
#     #Training  and product recognition -----------------------------------
#     FD("training_sample", BoolT, nan, 
#        "This listing is a training sample if `True`."),
#     FD("search_tasks", ListT(StrT), None, 
#        "List of task IDs (strings) of search tasks, "
#        "that returned this listing."),
#     FD("expected_products", ListT(StrT), None, 
#        "List of product IDs (strings)."),
#     FD("products", ListT(StrT), None, 
#        "Products in this listing."),
#     FD("products_absent", ListT(StrT), None, 
#        "Products not in this listing. List of product IDs (strings)."),
#     #Images --------------------------------------------------------------
#     FD("thumbnail", StrT, None, 
#        "URL of small image."),
#     FD("image", StrT, None, 
#        "URL of large image."),
#     #Product description --------------------------------------------------
#     FD("title", StrT, None, 
#        "Short description of listing."),
#     FD("description", StrT, None, 
#        "Long description of listing."),
#     FD("prod_spec", DictT(StrT,StrT), None, 
#        "product specific name value pairs (dict), for example: "
#        "``{'megapixel': '12'}``. The ``ItemSpecifics`` on Ebay."),    
#    # Status values ------------------------------------------------------
#     FD("active", BoolT, nan, 
#        "You can still buy the item if True"),
#     FD("sold", BoolT, nan, 
#        "Successful sale if ``True``."),
#     FD("currency", StrT, None, 
#        "Currency for price EUR, USD, ..."),
#     FD("price", FloatT, nan, 
#        "Price of listing (all items together)."),
#     FD("shipping", FloatT, nan, 
#        "Shipping cost"),
#     FD("type", StrT, None, 
#        "auction, fixed-price, unknown"),
#     FD("time", StrT, None, 
#        "Time when price is/was valid. End time in case of auctions."),
#     FD("location", StrT, None, 
#        "Location of item (pre sale)"),
#     FD("postcode", StrT, None, 
#        "Postal code of location"),
#     FD("country", StrT, None, 
#        "Country of item location."),
#     FD("condition", FloatT, nan, 
#        "1.: new, 0.: completely unusable"),
#     FD("seller", StrT, None, 
#        "User name of seller."),
#     FD("buyer", StrT, None, 
#        "User name of buyer."),
#     #Additional ----------------------------------------------------------
#     FD("server", StrT, None, 
#        "String to identify the server."),
#     FD("server_id", StrT, None, 
#        "ID of listing on the server."),
#    #TODO: Remove? This is essentially ``not active``.
#    FD("final_price", BoolT, nan, 
#        "If True: This is the final price of the auction."),
#     FD("url_webui", StrT, None, 
#        "Link to web representation of listing."),
#     #TODO: include bid_count?
#     ])


#TODO: Create function ``make_listing_id``.

