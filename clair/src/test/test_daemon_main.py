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
Test the deamon's top level object.
"""

from __future__ import division
from __future__ import absolute_import  
            
import pytest #contains `skip`, `fail`, `raises`, `config`

import os
import os.path as path
import glob
import time
from datetime import datetime

from numpy import isnan, nan
import pandas as pd

import logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime



def relative(*path_components):
    "Create file a path that is relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_components))


def test_MainObj_compute_next_due_time():
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
    
    
def test_MainObj_execute_tasks():
    """Test MainObj.execute_tasks"""
    from clair.daemon_main import MainObj
    from clair.coredata import Product, SearchTask, UpdateTask

    conf_dir = relative("..")
    data_dir = None
    
    #Create product information and search tasks 
    m = MainObj(conf_dir, data_dir)
    m.add_products([Product("nikon-d90", "Nikon D90", "DSLR Camera", 
                            None, None),
                    Product("nikon-d70", "Nikon D70", "DSLR Camera", 
                            None, None)])
    m.add_tasks([SearchTask("s-nikon-d90", datetime(2000,1,1), "ebay-de", 
                            "Nikon D90", "daily", 5, 10, 500, "EUR", 
                            ["nikon-d90"]),
                 SearchTask("s-nikon-d70", datetime(2000,1,1), "ebay-de", 
                            "Nikon D70", "daily", 5, 10, 500, "EUR", 
                            ["nikon-d70"])])
    
    #Execute the search tasks
    m.execute_tasks()
    print m.tasks
    print m.listings[["title", "price", "sold", "time"]].to_string()
    
    #Create an update task, that updates all listings immediately, 
    # and is executed only once
    upd_listings = m.listings["id"]
    m.add_tasks([UpdateTask("update-1", datetime(2000,1,1), "ebay-de", None, 
                           upd_listings)])
    
    #Execute the update task
    m.execute_tasks()
    print m.tasks
    print m.listings[["title", "price", "sold", "time", "server"]].to_string()
    
    #The search tasks must still exist, but the update task must be deleted
    assert len(m.tasks) == 2
    #There must be about 10 listings, 5 from each search task
    assert 8 <= len(m.listings) <= 10 #fewer listings: variants of the same item are removed
    
#    print m.listings[["description", "price"]].to_string()
    wakeup_time, sleep_sec = m.compute_next_wakeup_time()
    
    print "wakeup_time:", wakeup_time, "sleep_sec:", sleep_sec
    
    print "finished!"

    
def test_MainObj_create_final_update_tasks():
    """Test MainObj.create_final_update_tasks"""
    from clair.daemon_main import MainObj
    from clair.coredata import Product, SearchTask

    conf_dir = relative("..")
    data_dir = None
    
    #Create product information and a search task
    m = MainObj(conf_dir, data_dir)
    m.add_products([Product("nikon-d90", "Nikon D90", "DSLR Camera", 
                            None, None)])
    m.add_tasks([SearchTask("nikon-d90", datetime(2000,1,1), "ebay-de", 
                            "Nikon D90", "daily", 30, 10, 500, "EUR", 
                            ["nikon-d90"])])
    
    #Execute the search task
    m.execute_tasks()
#    print m.tasks
#    print m.listings[["title", "price", "sold", "time"]].to_string()
    
    #Create update tasks to get the final price of the listings
    m.create_final_update_tasks()
#    print m.tasks
    assert len(m.tasks) == 3
    assert 0.8 * 30 <= len(m.listings) <= 30
    
    #The tasks must be created only once
    m.create_final_update_tasks()
    assert len(m.tasks) == 3
    
    #continuous operation must be possible
    m.tasks["nikon-d90"].due_time = datetime(2000,1,1)
    m.execute_tasks()
    m.create_final_update_tasks()
    print m.tasks
    print m.listings[["title", "price", "sold", "time"]].to_string()
    
    print "finished!"
    

def experiment_MainObj_main_download_listings():
    """Test MainObj.create_final_update_tasks"""
#    pytest.skip("Test goes into infinite loop.") #IGNORE:E1101
    
    from clair.daemon_main import MainObj

    conf_dir = relative("../../example-data")
    data_dir = relative("../../example-data")
    
    m = MainObj(conf_dir, data_dir)
    
    m.main_download_listings()
    
    print "finished!"



if __name__ == "__main__":
#    test_MainObj_compute_next_due_time()
#    test_MainObj_execute_tasks()
#    test_MainObj_create_final_update_tasks()

    experiment_MainObj_main_download_listings()
    
    pass
