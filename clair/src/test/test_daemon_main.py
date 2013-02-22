# -*- coding: utf-8 -*-
###############################################################################
#    Clair - Project to discover prices on e-commerce sites.                  #
#                                                                             #
#    Copyright (C) 2013 by Eike Welk                                          #
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
Put module description here.
"""

from __future__ import division
from __future__ import absolute_import  
            
#import pytest #contains `skip`, `fail`, `raises`, `config`
import os
import glob
import os.path as path
from numpy import isnan, nan
from datetime import datetime

import pandas as pd


def relative(*path_components):
    "Create file a path that is relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_components))


def test_execute_tasks():
    """Test MainObj.execute_tasks"""
    from clair.daemon_main import MainObj
    from clair.coredata import Product, SearchTask, UpdateTask

    conf_dir = relative("..")
    data_dir = None
    
    m = MainObj(conf_dir, data_dir)
    m.add_products([Product("nikon-d90", "Nikon D90", "DSLR Camera", 
                            None, None),
                    Product("nikon-d70", "Nikon D70", "DSLR Camera", 
                            None, None)])
    m.add_tasks([SearchTask("nikon-d90", datetime(2000,1,1), "ebay-de", "daily", 
                            "Nikon D90", 5, 10, 500, "EUR", ["nikon-d90"]),
                 SearchTask("nikon-d70", datetime(2000,1,1), "ebay-de", "daily", 
                            "Nikon D70", 5, 10, 500, "EUR", ["nikon-d70"])])
    
    m.execute_tasks()
    print m.tasks
    print m.listings[["title", "price", "sold", "time"]].to_string()
    
    upd_listings = m.listings["id"]
    m.add_tasks([UpdateTask("update-1", datetime(2000,1,1), "ebay-de", None, 
                           upd_listings)])    
    m.execute_tasks()
    print m.tasks
    print m.listings[["title", "price", "sold", "time", "server"]].to_string()
    
    assert len(m.tasks) == 2
    assert 8 <= len(m.listings) <= 10 #fewer listings possible, variants of the same item are removed
    
    print "finished!"

    
    
def test_compute_next_due_time():
    """Test MainObj.compute_next_due_time"""
    from clair.daemon_main import MainObj
    
    m = MainObj("..", "..")
    
    #Without random the new times must be on the start of the interval
    t1 =  m.compute_next_due_time(datetime(2000, 1, 1, 0, 0), "monthly")
    print t1
    assert t1 == datetime(2000, 2, 1, 0, 0)
    t1 =  m.compute_next_due_time(datetime(2000, 1, 10, 20, 15), "monthly")
    print t1
    assert t1 == datetime(2000, 2, 1, 0, 0)
    
    t1 =  m.compute_next_due_time(datetime(2000, 1, 1, 20, 15), "weekly")
    print t1
    assert t1 == datetime(2000, 1, 3, 0, 0) #Monday 2000-1-3
    
    t1 =  m.compute_next_due_time(datetime(2000, 1, 1, 0, 0), "daily")
    print t1
    assert t1 == datetime(2000, 1, 2, 0, 0)
    t1 =  m.compute_next_due_time(datetime(2000, 1, 1, 20, 15), "daily")
    print t1
    assert t1 == datetime(2000, 1, 2, 0, 0)
    
    t1 =  m.compute_next_due_time(datetime(2000, 1, 1, 20, 0), "hourly")
    print t1
    assert t1 == datetime(2000, 1, 1, 21, 0)
    t1 =  m.compute_next_due_time(datetime(2000, 1, 1, 20, 15), "hourly")
    print t1
    assert t1 == datetime(2000, 1, 1, 21, 0)
    
    t = datetime(2000, 1, 1, 20, 15)
    times = [t]
    for _ in range(20):
        t = m.compute_next_due_time(t, "day", True)
        times.append(t)
#    print times
    times = pd.Series(times)
    print times
    diff = times.diff()
    print diff
    
    print "finished!"
    
    
def test_create_final_update_tasks():
    """Test MainObj.create_final_update_tasks"""
    from clair.daemon_main import MainObj
    from clair.coredata import Product, SearchTask

    conf_dir = relative("..")
    data_dir = None
    
    m = MainObj(conf_dir, data_dir)
    m.add_products([Product("nikon-d90", "Nikon D90", "DSLR Camera", 
                            None, None)])
    m.add_tasks([SearchTask("nikon-d90", datetime(2000,1,1), "ebay-de", "daily", 
                            "Nikon D90", 25, 10, 500, "EUR", ["nikon-d90"])])
    
    m.execute_tasks()
#    print m.tasks
    print m.listings[["title", "price", "sold", "time"]].to_string()
     
    m.create_final_update_tasks()
    
    print "finished!"
    
    
    
if __name__ == "__main__":
#    test_execute_tasks()
#    test_compute_next_due_time()
    test_create_final_update_tasks()
    
    pass
