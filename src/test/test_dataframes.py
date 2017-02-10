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
Test module ``dataframes``, which contains definitions of the the 
``pandas.DataFrame`` objects that store the application's important data in 2D
tables.
"""
            
#import pytest #contains `skip`, `fail`, `raises`, `config` #IGNORE:W0611


from numpy import isnan #, nan #IGNORE:E0611
#from pandas.util.testing import assert_frame_equal
from datetime import datetime
import pandas as pd

#import time
#import logging
#from logging import info
#logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
#                    level=logging.DEBUG)
##Time stamps must be in UTC
#logging.Formatter.converter = time.gmtime



def make_test_listings():
    """
    Create a DataFrame with some data.
    
    Contains 3 listings: 
    row 0: contains realistic data; rows 1, 2 contain mainly None, nan.
    """
    from clair.dataframes import make_listing_frame
    
    fr = make_listing_frame(3)
    #All listings need unique ids
    fr["id"] = ["eb-123", "eb-456", "eb-457"]
    
    fr.ix[0, "training_sample"] = True 
    fr.ix[0, "search_tasks"] = ["s-nikon-d90"]
#    fr.ix[0, "query_string"] = "Nikon D90"

    fr.set_value(0, "expected_products", ["nikon-d90", "nikon-sb-24"])
    fr.ix[0, "products"] = ["nikon-d90"]
    fr.ix[0, "products_absent"] = ["nikon-sb-24"]
    
    fr.ix[0, "thumbnail"] = "www.some.site/dir/to/thumb.pg"
    fr.ix[0, "image"] = "www.some.site/dir/to/img.pg"
    fr["title"] = ["Nikon D90 super duper!", "<>müäh", None]
    fr.ix[0, "description"] = "Buy my old Nikon D90 camera <b>now</b>!"
    fr.set_value(0, "prod_spec", {"Marke":"Nikon", "Modell":"D90"})
    fr.ix[0, "active"] = False
    fr.ix[0, "sold"] = False
    fr.ix[0, "currency"] = "EUR"
    fr.ix[0, "price"]    = 400.
    fr.ix[0, "shipping"] = 12.
    fr.ix[0, "type"] = "auction"
    fr["time"] = [datetime(2013,1,10), datetime(2013,2,2), datetime(2013,2,3)]
    fr.ix[0, "location"] = "Köln"
    fr.ix[0, "postcode"] = "50667"
    fr.ix[0, "country"] = "DE"
    fr.ix[0, "condition"] = 0.7
    fr.ix[0, "server"] = "Ebay-Germany"
    fr.ix[0, "server_id"] = "123" #ID of listing on server
    fr.ix[0, "final_price"] = True
#    fr["data_directory"] = ""
    fr.ix[0, "url_webui"] = "www.some.site/dir/to/web-page.html"
#     fr.ix[0, "server_repr"] = nan
    #Put our IDs into index
    fr.set_index("id", drop=False, inplace=True, 
                 verify_integrity=True)
#    print fr
    return fr

    
def assert_frames_equal(fr1, fr2):
    """
    Asserts that two data frame objects are equal. 
    Handles ``nan`` and ``None`` right.
    """
    assert all(fr1.columns == fr2.columns)
    
    #Compare the two DataFrame objects. Complications:
    #* (nan == nan) == False
    #* (None == None) == False; Special treatment of None inside DataFrame.
    for col in fr1.columns:
        for i in range(len(fr1.index)):
            try:
                assert fr1[col][i] == fr2[col][i]
            except AssertionError:
                if isinstance(fr1[col][i], float) and \
                   isinstance(fr2[col][i], float) and \
                   isnan(fr1[col][i]) and isnan(fr2[col][i]):
                    continue
                
                print("col =", repr(col), "; i =", i)
                print("fr1[col][i] =", fr1[col][i], \
                      "; type(fr1[col][i]) =", type(fr1[col][i]))  
                print("fr2[col][i] =", fr2[col][i], \
                       "; type(fr2[col][i]) =", type(fr2[col][i]))
                    
                raise


#def test_make_price_frame():
#    "Test creation of a empty data frame of prices."
#    from clair.coredata import PriceConstants, make_price_frame
#    print "start"
#    
#    prices = make_price_frame(5)
#    
#    assert len(prices) == 5
#    assert isnan(prices.ix[0, "price"])
#    assert prices.ix[1, "currency"] is None 
#    assert prices.ix[2, "time"] is None 
#    assert prices.ix[3, "product"] is None 
#    assert prices.ix[4, "listing"] is None 
#    assert prices.ix[0, "type"] is None 
#    assert prices.ix[1, "id"] is None 
#    
#    prices["price"] = 2.5
#    prices.ix[2,"product"] = "foo-bar"
#    prices.ix[3, "listing"] = "baz-boo"
#    assert all(prices["price"] == 2.5)
#    assert prices["product"][2] == "foo-bar"
#    assert prices.ix[3, "listing"] == "baz-boo"
#    
#    print prices
#    print PriceConstants.comments
#    print "Finished"
    

def test_make_data_series():
    print("Start")
    from clair.descriptors import (StrD, IntD, FloatD, BoolD, DateTimeD, 
                                   ListD, DictD, FieldDescriptor)
    from clair.dataframes import make_data_series

    fd = FieldDescriptor("foo", FloatD, None, "foo data")
    s = make_data_series(fd, 3)
    s[1] = 1.4
    print(s)
    assert len(s) == 3 
    assert isnan(s[0])
    assert s[1] == 1.4
    
    fd = FieldDescriptor("foo", FloatD, 0., "foo data")
    s = make_data_series(fd, 3)
    s[1] = 4.2
    print(s)
    assert len(s) == 3
    assert s[0] == 0
    assert s[1] == 4.2

    fd = FieldDescriptor("foo", IntD, None, "foo data")
    s = make_data_series(fd, 4)
    s[1] = 23
    print(s)
    assert len(s) == 4
    assert isnan(s[0])
    assert s[1] == 23
    
    fd = FieldDescriptor("foo", BoolD, None, "foo data")
    s = make_data_series(fd, 3)
    s[1] = True
    print(s)
    assert len(s) == 3
    assert isnan(s[0])
    assert s[1] == True

    fd = FieldDescriptor("foo", DateTimeD, None, "foo data")
    s = make_data_series(fd, 3)
    s[1] = pd.Timestamp('2001-01-23 12:30:00')
    print(s)
    assert len(s) == 3
#     assert isnan(s[0])
    assert s[1] == pd.Timestamp('2001-01-23 12:30:00')

    fd = FieldDescriptor("foo", ListD(StrD), None, "foo data")
    s = make_data_series(fd, 3)
    s[1] = ["foo", "bar"]
    print(s)
    assert len(s) == 3
    assert isnan(s[0])
    assert s[1] == ["foo", "bar"]
    
    
def test_make_data_frame():
    print("Start")
    from clair.descriptors import StrD, FloatD, FieldDescriptor, TableDescriptor
    from clair.dataframes import make_data_frame

    FD = FieldDescriptor
    td = TableDescriptor("foo-table", "1.0", "foot", 
                         "A table for testing purposes.", 
                         [FD("foo", FloatD, None, "foo data"),
                          FD("bar", StrD, None, "bar data")])
    df = make_data_frame(td, 3)
    df.at[1, "foo"] = 23
    df.at[2, "bar"] = "a"
    print(df)
    print("dtypes:\n", df.dtypes)
    
    assert df.shape == (3, 2)
    assert isnan(df.at[0, "bar"])
    assert df.at[1, "foo"] == 23
    assert df.at[2, "bar"] == "a"


def test_make_listing_frame():
    print("Start")
    from clair.dataframes import make_listing_frame
    
    lf = make_listing_frame(10)
    assert len(lf.index) == 10


if __name__ == "__main__":
    test_make_data_series()
#     test_make_data_frame()
    
    pass #IGNORE:W0107
