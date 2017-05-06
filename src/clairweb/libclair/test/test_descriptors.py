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
Test module ``descriptors``, which contains tools to define the structure 
of a table or database.
"""


  
            
#import pytest #contains `skip`, `fail`, `raises`, `config` #IGNORE:W0611


#from numpy import isnan #, nan #IGNORE:E0611
#from pandas.util.testing import assert_frame_equal

#import time
#import logging
#from logging import info
#logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
#                    level=logging.DEBUG)
##Time stamps must be in UTC
#logging.Formatter.converter = time.gmtime


def test_TypeTag_s():
    print("Start")
    from numpy import nan           #IGNORE:E0611
    from datetime import datetime
    from libclair.descriptors import \
        NoneD, StrD, IntD, FloatD, DateTimeD, SumTypeD, ListD, DictD

    assert NoneD.is_py_instance(None)
    assert not NoneD.is_py_instance(3)
    
    assert StrD.is_py_instance("foo")
    assert not StrD.is_py_instance(3)
    
    assert IntD.is_py_instance(23)
    assert not IntD.is_py_instance(23.5)
    
    assert FloatD.is_py_instance(4.2)
    assert FloatD.is_py_instance(nan)
    assert not FloatD.is_py_instance(3)
    
    assert DateTimeD.is_py_instance(datetime(2000, 1, 1))
    assert not DateTimeD.is_py_instance(3)

    ts = SumTypeD(IntD, FloatD)
    assert ts.is_py_instance(1)
    assert ts.is_py_instance(1.41)
    assert not ts.is_py_instance("a")
    
    tl = ListD(FloatD)
    assert tl.is_py_instance([])
    assert tl.is_py_instance([1.2, 3.4])
    assert not tl.is_py_instance([1, 3])
    
    tl2 = ListD(SumTypeD(FloatD, IntD))
    assert tl2.is_py_instance([1.2, 3, 4])
    assert not tl.is_py_instance([1, "a"])
    
    tm = DictD(StrD, IntD)
    assert tm.is_py_instance({})
    assert tm.is_py_instance({"foo": 2, "bar": 3})
    assert not tm.is_py_instance({"foo": 2, "bar": 3.1415})
    

def test_FieldDescriptor():
    print("Start")
    from libclair.descriptors import FieldDescriptor, IntD
    
    FieldDescriptor("foo", IntD, 1, "A foo integer.")
    FieldDescriptor("foo", IntD, None, "A foo integer or None.")


def test_TableDescriptor():
    print("Start")
    from libclair.descriptors import TableDescriptor, FieldDescriptor, IntD

    F = FieldDescriptor
    TableDescriptor("foo_table", "1.0", "fot", "A table of foo elements",
                    [F("foo1", IntD, 0, "A foo integer."),
                     F("foo2", IntD, None, "A foo integer or None.")
                    ])


if __name__ == "__main__":
#     test_TypeTag_s()
#     test_FieldDescriptor()
#     test_TableDescriptor()
    
    pass #IGNORE:W0107
