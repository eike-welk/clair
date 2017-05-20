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

            
import pytest #contains `skip`, `fail`, `raises`, `config`

import os
import os.path as path
# import sys
import time
# from datetime import datetime

# import numpy as np
# import pandas as pd
import django

# #Configure logging to print nice messages to stderr
import logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime



def relative(*path_components):
    "Create file a path that is relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_components))


# def test_MainObj_compute_next_due_time():
#     """Test DaemonMain.compute_next_due_time"""
#     from clair.daemon import DaemonMain
#     
#     m = DaemonMain("..", "..")
#     
#     #Without random the new times must be on the start of the interval
#     t1 =  m.compute_next_due_time(datetime(2000, 1, 1, 0, 0), "monthly")
#     print(t1)
#     assert t1 == datetime(2000, 2, 1, 0, 0)
#     t1 =  m.compute_next_due_time(datetime(2000, 1, 10, 20, 15), "monthly")
#     print(t1)
#     assert t1 == datetime(2000, 2, 1, 0, 0)
#     
#     t1 =  m.compute_next_due_time(datetime(2000, 1, 1, 20, 15), "weekly")
#     print(t1)
#     assert t1 == datetime(2000, 1, 3, 0, 0) #Monday 2000-1-3
#     
#     t1 =  m.compute_next_due_time(datetime(2000, 1, 1, 0, 0), "daily")
#     print(t1)
#     assert t1 == datetime(2000, 1, 2, 0, 0)
#     t1 =  m.compute_next_due_time(datetime(2000, 1, 1, 20, 15), "daily")
#     print(t1)
#     assert t1 == datetime(2000, 1, 2, 0, 0)
#     
#     t1 =  m.compute_next_due_time(datetime(2000, 1, 1, 20, 0), "hourly")
#     print(t1)
#     assert t1 == datetime(2000, 1, 1, 21, 0)
#     t1 =  m.compute_next_due_time(datetime(2000, 1, 1, 20, 15), "hourly")
#     print(t1)
#     assert t1 == datetime(2000, 1, 1, 21, 0)
#     
# #    t = datetime(2000, 1, 1, 20, 15)
# #    times = [t]
# #    for _ in range(20):
# #        t = m.compute_next_due_time(t, "day", True)
# #        times.append(t)
# ##    print times
# #    times = pd.Series(times)
# #    print times
# #    diff = times.diff()
# #    print diff
#     
#     print("finished!")
    
    
def test_MainObj_execute_tasks():
    """Test DaemonMain.execute_tasks"""
    print('Start: test_MainObj_execute_tasks')

    from collect.daemon import DaemonMain
    from collect.models import SearchTask
    
    # Get one search task
    task = SearchTask.objects.all()[0]

    #Execute the search tasks
    m = DaemonMain()
    task_ids = m.execute_search_task(task)
    print('Number of listings: ', len(task_ids))

    assert len(task_ids) > 20

    print("Finished!")

    
# def test_MainObj_create_final_update_tasks():
#     """Test DaemonMain.create_final_update_tasks"""
#     from clair.daemon import DaemonMain
#     from clair.coredata import Product, SearchTask
# 
#     conf_dir = relative("..")
#     data_dir = None
#     
#     #Create product information and a search task
#     m = DaemonMain(conf_dir, data_dir)
#     m.data.set_products([Product("nikon-d90", "Nikon D90", "DSLR Camera", 
#                             None, None)])
#     m.data.add_tasks([SearchTask("nikon-d90", datetime(2000,1,1), "ebay-de", 
#                             "Nikon D90", "daily", 30, 10, 500, "EUR", 
#                             ["nikon-d90"])])
#     
#     #Execute the search task
#     m.execute_tasks()
# #    print m.data.tasks
# #    print m.data.listings[["title", "price", "sold", "time"]].to_string()
#     
#     #Create update tasks to get the final price of the listings
#     m.create_final_update_tasks()
# #    print m.data.tasks
#     assert len(m.data.tasks) == 3
#     assert 0.8 * 30 <= len(m.data.listings) <= 30
#     
#     #The tasks must be created only once
#     m.create_final_update_tasks()
#     assert len(m.data.tasks) == 3
#     
#     #continuous operation must be possible
#     m.data.tasks[0].due_time = datetime(2000,1,1)
#     m.execute_tasks()
#     m.create_final_update_tasks()
#     print(m.data.tasks)
#     print(m.data.listings[["title", "price", "sold", "time"]].to_string())
#     
#     print("finished!")
   


if __name__ == "__main__":
    #One can't use models without this
    os.environ['DJANGO_SETTINGS_MODULE'] = 'clairweb.settings'
    django.setup()

#     test_MainObj_compute_next_due_time()
    test_MainObj_execute_tasks()
#    test_MainObj_create_final_update_tasks()
#    test_MainObj_main_download_listings()
#    test_CommandLineHandler_parse_command_line()
    
#    experiment_MainObj_main_download_listings()
    
    pass
