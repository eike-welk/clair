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

from __future__ import division
from __future__ import absolute_import  
            
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
    print "Start"
    from numpy import nan           #IGNORE:E0611
    from datetime import datetime
    from clair.descriptors import \
        NoneT, StrT, IntT, FloatT, DateTimeT, SumT, ListT, DictT

    assert NoneT.is_instance_T(None)
    assert not NoneT.is_instance_T(3)
    
    assert StrT.is_instance_T("foo")
    assert not StrT.is_instance_T(3)
    
    assert IntT.is_instance_T(23)
    assert not IntT.is_instance_T(23.5)
    
    assert FloatT.is_instance_T(4.2)
    assert FloatT.is_instance_T(nan)
    assert not FloatT.is_instance_T(3)
    
    assert DateTimeT.is_instance_T(datetime(2000, 1, 1))
    assert not DateTimeT.is_instance_T(3)

    ts = SumT(IntT, FloatT)
    assert ts.is_instance_T(1)
    assert ts.is_instance_T(1.41)
    assert not ts.is_instance_T("a")
    
    tl = ListT(FloatT)
    assert tl.is_instance_T([])
    assert tl.is_instance_T([1.2, 3.4])
    assert not tl.is_instance_T([1, 3])
    
    tl2 = ListT(SumT(FloatT, IntT))
    assert tl2.is_instance_T([1.2, 3, 4])
    assert not tl.is_instance_T([1, "a"])
    
    tm = DictT(StrT, IntT)
    assert tm.is_instance_T({})
    assert tm.is_instance_T({"foo": 2, "bar": 3})
    assert not tm.is_instance_T({"foo": 2, "bar": 3.1415})
    

def test_FieldDescriptor():
    print "Start"
    from clair.descriptors import FieldDescriptor, IntT
    
    FieldDescriptor("foo", IntT, 1, "A foo integer.")
    FieldDescriptor("foo", IntT, None, "A foo integer or None.")


def test_TableDescriptor():
    print "Start"
    from clair.descriptors import TableDescriptor, FieldDescriptor, IntT

    F = FieldDescriptor
    TableDescriptor("foo_table", "1.0", "fot", "A table of foo elements",
                    [F("foo1", IntT, 0, "A foo integer."),
                     F("foo2", IntT, None, "A foo integer or None.")
                    ])


if __name__ == "__main__":
    test_TypeTag_s()
#    test_FieldDescriptor()
#    test_TableDescriptor()
    
    pass #IGNORE:W0107
