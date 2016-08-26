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

from __future__ import division
from __future__ import absolute_import  
            
#import pytest #contains `skip`, `fail`, `raises`, `config` #IGNORE:W0611


from numpy import isnan #, nan #IGNORE:E0611
#from pandas.util.testing import assert_frame_equal

#import time
#import logging
#from logging import info
#logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
#                    level=logging.DEBUG)
##Time stamps must be in UTC
#logging.Formatter.converter = time.gmtime


def test_make_data_series():
    print "Start"
    from clair.descriptors import StrT, IntT, FloatT, BoolT, ListT, DictT, FieldDescriptor
    from clair.dataframes import make_data_series

    fd = FieldDescriptor("foo", FloatT, None, "foo data")
    s = make_data_series(fd, 3)
    s[1] = 1.4
    print s
    assert len(s) == 3 
    assert isnan(s[0])
    assert s[1] == 1.4

    fd = FieldDescriptor("foo", IntT, None, "foo data")
    s = make_data_series(fd, 4)
    s[1] = 23
    print s
    assert len(s) == 4
    assert isnan(s[0])
    assert s[1] == 23
    
    fd = FieldDescriptor("foo", BoolT, None, "foo data")
    s = make_data_series(fd, 3)
    s[1] = True
    print s
    assert len(s) == 3
    assert isnan(s[0])
    assert s[1] == True

    fd = FieldDescriptor("foo", ListT(StrT), None, "foo data")
    s = make_data_series(fd, 3)
    s[1] = ["foo", "bar"]
    print s
    assert len(s) == 3
    assert isnan(s[0])
    assert s[1] == ["foo", "bar"]

    fd = FieldDescriptor("foo", FloatT, 0., "foo data")
    s = make_data_series(fd, 3)
    s[1] = 4.2
    print s
    assert len(s) == 3
    assert s[0] == 0
    assert s[1] == 4.2
    
    
def test_make_data_frame():
    print "Start"
    from clair.descriptors import StrT, FloatT, FieldDescriptor, TableDescriptor
    from clair.dataframes import make_data_frame

    FD = FieldDescriptor
    td = TableDescriptor("foo-table", "1.0", "foot", 
                         "A table for testing purposes.", 
                         [FD("foo", FloatT, None, "foo data"),
                          FD("bar", StrT, None, "bar data")])
    df = make_data_frame(td, 3)
    df.at[1, "foo"] = 23
    df.at[2, "bar"] = "a"
    print df
    print df.dtypes
    
    assert len(df.index) == 3
    assert len(df.columns) == 2
    assert isnan(df.at[0, "bar"])
    assert df.at[1, "foo"] == 23
    assert df.at[2, "bar"] == "a"



if __name__ == "__main__":
#    test_make_data_series()
    test_make_data_frame()
    
    pass #IGNORE:W0107
