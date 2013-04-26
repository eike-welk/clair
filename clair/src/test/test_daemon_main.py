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
    m.data.set_products([Product("nikon-d90", "Nikon D90", "DSLR Camera", 
                                 None, None),
                         Product("nikon-d70", "Nikon D70", "DSLR Camera", 
                                 None, None)])
    m.data.add_tasks([SearchTask("s-nikon-d90", datetime(2000,1,1), "ebay-de", 
                                 "Nikon D90", "daily", 5, 150, 500, "EUR", 
                                 ["nikon-d90"]),
                      SearchTask("s-nikon-d90-2", datetime(2000,1,1), "ebay-de", 
                                 "Nikon D90", "daily", 5, 150, 500, "EUR", 
                                 ["nikon-d90"]),
                      SearchTask("s-nikon-d70", datetime(2000,1,1), "ebay-de", 
                                 "Nikon D70", "daily", 5, 50, 500, "EUR", 
                                 ["nikon-d70"])])
    
    #Execute the search tasks
    m.execute_tasks()
    print m.data.tasks
    print m.data.listings[["title", "price", "sold", "time"]].to_string()
    
    #Create an update task, that updates all listings immediately, 
    # and is executed only once
    upd_listings = m.data.listings["id"]
    m.data.add_tasks([UpdateTask("update-1", datetime(2000,1,1), "ebay-de", 
                                 None, upd_listings)])
    
    #Execute the update task
    m.execute_tasks()
    print m.data.tasks
    print m.data.listings[["title", "price", "sold", "time", "server"]].to_string()
    #    print m.listings[["description", "price"]].to_string()
    
    wakeup_time, sleep_sec = m.compute_next_wakeup_time()
    print "wakeup_time:", wakeup_time, "sleep_sec:", sleep_sec
    
    #The search tasks must still exist, but the update task must be deleted
    assert len(m.data.tasks) == 3
    
    #There must be about 10 listings, 5 from each search task, 
    #but "s-nikon-d90" and "s-nikon-d90-2" have the same search string, and 
    #should find the same listings
    assert 8 <= len(m.data.listings) <= 12 #fewer listings: variants of the same item are removed
    
    #Test correct behavior if multiple search tasks find the same listings:
    #There is a 2nd ``SearchTask`` that also searches for "Nikon D90",
    #but with different name: "s-nikon-d90-2".
    #This this task must appear in the "search_tasks" field.   
    tasks_lens = [0, 0, 0, 0] #Histogram of length of "search_tasks" list
    prods_lens = [0, 0, 0, 0] #Histogram of length of "expected_products" list
    n_2_d90 = 0 #Number of listings that were found by "s-nikon-d90" and "s-nikon-d90-2".
    for _, listing in m.data.listings.iterrows():
#        print listing
        #Compute histogram of length of "search_tasks" list
        n_tasks = len(listing["search_tasks"])
        tasks_lens[n_tasks] += 1
        #Compute histogram of length of "search_tasks" list
        n_prods = len(listing["expected_products"])
        prods_lens[n_prods] += 1
        #how many listings have "s-nikon-d90" and "s-nikon-d90-2" in "search_tasks" field
        if "s-nikon-d90" in listing["search_tasks"] and \
           "s-nikon-d90-2" in listing["search_tasks"]:
            n_2_d90 += 1
    #These tests may sometimes fail, some listings contain D90 and D70 in 
    #their title.
    print "tasks_lens", tasks_lens
    assert tasks_lens[0] == 0 #listings without a search task: impossible
    assert 4 <= tasks_lens[1] <= 5 #listings with one search task: D70
    assert 4 <= tasks_lens[2] <= 5 #listings with two search tasks:
    #                               "s-nikon-d90", "s-nikon-d90-2"
    assert 0 <= tasks_lens[3] <= 1 #listings with three search tasks: unlikely
    #listings that were found by search tasks: "s-nikon-d90" and "s-nikon-d90-2"
    assert n_2_d90 == 5
    print "prods_lens", prods_lens
    assert prods_lens[0] == 0 #listings without an expected product: impossible
    assert 8 <= prods_lens[1] <= 10 #listings with one product: D70 or D90
    assert 0 <= prods_lens[2] <= 1  #listings with two products: unlikely
    assert prods_lens[3] == 0 #listings with three products: impossible
    
    #Test if update has really happened: Only update tasks download descriptions
    assert all([d is not None for d in listing["description"]])

    print "finished!"

    
def test_MainObj_create_final_update_tasks():
    """Test MainObj.create_final_update_tasks"""
    from clair.daemon_main import MainObj
    from clair.coredata import Product, SearchTask

    conf_dir = relative("..")
    data_dir = None
    
    #Create product information and a search task
    m = MainObj(conf_dir, data_dir)
    m.data.set_products([Product("nikon-d90", "Nikon D90", "DSLR Camera", 
                            None, None)])
    m.data.add_tasks([SearchTask("nikon-d90", datetime(2000,1,1), "ebay-de", 
                            "Nikon D90", "daily", 30, 10, 500, "EUR", 
                            ["nikon-d90"])])
    
    #Execute the search task
    m.execute_tasks()
#    print m.data.tasks
#    print m.data.listings[["title", "price", "sold", "time"]].to_string()
    
    #Create update tasks to get the final price of the listings
    m.create_final_update_tasks()
#    print m.data.tasks
    assert len(m.data.tasks) == 3
    assert 0.8 * 30 <= len(m.data.listings) <= 30
    
    #The tasks must be created only once
    m.create_final_update_tasks()
    assert len(m.data.tasks) == 3
    
    #continuous operation must be possible
    m.data.tasks[0].due_time = datetime(2000,1,1)
    m.execute_tasks()
    m.create_final_update_tasks()
    print m.data.tasks
    print m.data.listings[["title", "price", "sold", "time"]].to_string()
    
    print "finished!"
   

@pytest.mark.skipif #IGNORE:E1101
def test_MainObj_main_download_listings():
    """Test MainObj.main_download_listings"""
    
    from clair.daemon_main import MainObj

    example_data = relative("../../example-data")
    conf_dir = relative("../../test-data/test-download-listings")
    data_dir = relative("../../test-data/test-download-listings")
    
    #Create a fresh copy of the example data
    os.system("rm -rf " + data_dir)
    os.system("cp -r " + example_data + " " + data_dir)
    
    m = MainObj(conf_dir, data_dir)
    
    m.main_download_listings(1)
    
    print "finished!"
    
    
def experiment_MainObj_main_download_listings():
    """Experiment with MainObj.main_download_listings"""
    
    from clair.daemon_main import MainObj

    conf_dir = relative("../../../../clair-data")
    data_dir = relative("../../../../clair-data")
#    conf_dir = relative("../../example-data-1")
#    data_dir = relative("../../example-data-1")
    
    m = MainObj(conf_dir, data_dir)
    
    m.main_download_listings(-1)
    
    print "finished!"



if __name__ == "__main__":
#    test_MainObj_compute_next_due_time()
#    test_MainObj_execute_tasks()
#    test_MainObj_create_final_update_tasks()
#    test_MainObj_main_download_listings()

    experiment_MainObj_main_download_listings()
    
    pass
