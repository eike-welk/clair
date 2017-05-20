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
Main module for the server and command line script.
"""


# import os
from os import path
# from datetime import datetime, timedelta
import time
# from random import randint
import logging

# import dateutil.rrule
# import pandas as pd
#import numpy as np
from django.conf import settings

from collect.get_ebay import EbayConnector
from collect.models import SearchTask, ListingFoundBy
import econdata.models
from libclair.dataframes import write_frame, make_data_frame
# from clair.coredata import SearchTask, UpdateTask, DataStore
# from clair.textprocessing import RecognizerController



# #Configure logging to print nice messages to stderr
# logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
#                     level=logging.DEBUG)
# #Time stamps must be in UTC
# logging.Formatter.converter = time.gmtime



class DaemonMain(object):
    """Main object for downloading listings from the Internet."""

    all_ebay_global_ids = {
       "EBAY-AT", "EBAY-AU", "EBAY-CH", "EBAY-DE", "EBAY-ENC", "EBAY-ES",
       "EBAY-FR", "EBAY-FRB", "EBAY-FRC", "EBAY-GB", "EBAY-HK", "EBAY-IE",
       "EBAY-IN", "EBAY-IT", "EBAY-MOT", "EBAY-MY", "EBAY-NL", "EBAY-NLB",
       "EBAY-PH", "EBAY-PL", "EBAY-SG", "EBAY-US", }
    "Legal values for Ebay's global ID."

    def __init__(self):
        base_dir = settings.BASE_DIR
        self.connector = EbayConnector(path.join(base_dir, 'ebay-sdk.apikey'))
    
#     def compute_next_due_time(self, curr_time, recurrence_pattern, 
#                               add_random=False):
#         """
#         Compute next due time for recurrent tasks.
#         
#         Parameters
#         ----------
#         
#         curr_time : datetime
#             Start time of the recurrence. Current time should be used.
#             
#         recurrence_pattern: str 
#             How often should the task be executed? One of:
#                 * "m", "month", "monthly"
#                 * "w", "week", "weekly"
#                 * "d", "day", "daily"
#                 * "h", "hour", "hourly"
#         
#         add_random: bool
#             If ``True``, add a random amount of time to the computed due time,
#             to avoid load spikes. 
#             If ``False``, the computed times are at the start of the interval,
#             for example at 00:00 o'clock for "daily" recurrence.
#             
#         Returns
#         -------
#         datetime
#             The new due time
#         """
#         bymonth = None; bymonthday = None; byweekday = None; byhour = None
#         byminute = 0; bysecond = 0
#         
#         recurrence_pattern = recurrence_pattern.lower()
#         if recurrence_pattern in ["m", "month", "monthly"]:
#             freq = dateutil.rrule.MONTHLY
#             byhour = 0
#             bymonthday = 1
#             rand_max = 15 * 24 * 60 * 60 #sec - 15 days
#         elif recurrence_pattern in ["w", "week", "weekly"]:
#             freq = dateutil.rrule.WEEKLY
#             byhour = 0
#             byweekday = 0
#             rand_max = 3.5 * 24 * 60 * 60 #sec - 3.5 days
#         elif recurrence_pattern in ["d", "day", "daily"]:
#             freq = dateutil.rrule.DAILY
#             byhour = 0
#             rand_max = 12 * 60 * 60 #sec - 12 hours
#         elif recurrence_pattern in ["h", "hour", "hourly"]:
#             freq = dateutil.rrule.HOURLY
#             rand_max = 30 * 60 #sec - 30 minutes
#         else:
#             raise ValueError("Unkown recurrence_pattern: " + 
#                              str(recurrence_pattern))
#         
#         rrule = dateutil.rrule.rrule(freq=freq, dtstart=curr_time, count=2, 
#                                      bymonth=bymonth, bymonthday=bymonthday, 
#                                      byweekday=byweekday, byhour=byhour, 
#                                      byminute=byminute, bysecond=bysecond,
#                                      cache=True)
#         new_time = rrule.after(curr_time)
#         
#         #Add add_random component.
#         if add_random:
#             rand_secs = randint(0, rand_max)
#             new_time += timedelta(seconds=rand_secs)
#         
#         return new_time
#     
#         
#     def compute_next_wakeup_time(self):
#         """
#         Compute time when application needs to wake up to execute next task.
#          
#         Loops over all tasks in ``self.tasks``.
#          
#         Returns
#         -------
#          
#         datetime, float
#          
#         * Time when next task is due
#         * Number of seconds to sleep until the next task is due.
#         """
#         wakeup_time = datetime(9999, 12, 31) #The last possible month
#         for task in self.data.tasks:
#             wakeup_time = min(task.due_time, wakeup_time)
#              
#         sleep_interval = wakeup_time - datetime.utcnow()
#         sleep_sec = max(sleep_interval.total_seconds(), 0.) 
#          
#         return wakeup_time, sleep_sec

    def execute_search_task(self, task):
        """Search for new listings. Executes a search task."""
        assert isinstance(task, SearchTask)
        logging.debug("Executing search task: '{id}'".format(id=task.id))
        start_time = time.time()
        
        if task.server not in self.all_ebay_global_ids:
            logging.error('Invalid server ID: "{sid}"'.format(sid=task.server))
            return []

        # Get the keywords from the product if a product is given. 
        if task.query_string:
            query_string = task.query_string
        elif task.product:
            query_string = task.product.name + ', ' + task.product.important_words
        else:
            logging.error('No keywords to search for.\n'
                          '``task.query_string`` and product are empty.')
            return []
        
        #Get new listings from server
        listings_found = self.connector.find_listings(
                                    keywords=query_string, 
                                    n_listings=task.n_listings, 
                                    ebay_site=task.server,
                                    price_min=task.price_min, 
                                    price_max=task.price_max, 
                                    currency=task.currency,
                                    time_from=None,
                                    time_to=None)
        #Fill in all details of the new listings
        listings_upd = self.connector.update_listings(listings_found, task.server)
        #Store the listings
        write_frame(listings_upd, econdata.models.Listing)

        # Store which listing has been found by which task
        found_by = make_data_frame(ListingFoundBy, len(listings_upd))
        found_by['task'] = task.id
        found_by['listing'] = listings_upd['id'].values
        write_frame(found_by, ListingFoundBy, fieldnames=['task', 'listing'], idnames=['task', 'listing'])

        end_time = time.time()
        delta_sec = end_time - start_time
        logging.info('Downloaded {num} listings in {dur} sec.'
                     .format(num=len(listings_upd), dur=delta_sec))
        return list(listings_upd["id"])

#     def execute_update_task(self, task):
#         """
#         Download the complete information of known listings. 
#         Executes an update task.
#         Tries to recognize products in updated tasks.
#         """
#         assert isinstance(task, UpdateTask)
#         logging.debug("Executing update task: '{id}'".format(id=task.id))
#         
#         #Download the tasks
#         lst_update = self.data.listings.ix[task.listings]
#         lst_update = self.connector.update_listings(lst_update)
#         lst_update["server"] = task.server
# #        lst_update["final_price"] = True #Use as flag, just to be sure
#         self.data.merge_listings(lst_update)
#         
#         #Recognize products
#         self.recognizers.recognize_products(lst_update.index, 
#                                             self.data.listings)
#         return list(lst_update["id"])
#         
#         
#     def execute_tasks(self):
#         """
#         Execute the due tasks in ``self.tasks``.
#         
#         Removes single shot tasks.
#         """
#         logging.info("Executing due tasks.")
#         now = datetime.utcnow()
#         dead_tasks = []
#         for itask, task in enumerate(self.data.tasks):
#             #Test is task due
#             if task.due_time > now:
#                 continue
#             
#             logging.info("Executing task: {}".format(task.id))
#             #Search for new listings
#             if isinstance(task, SearchTask):
#                 self.execute_search_task(task)
#             #Update known listings
#             elif isinstance(task, UpdateTask):
#                 self.execute_update_task(task)
#             else:
#                 raise TypeError("Unknown task type:" + str(type(task)) + 
#                                 "\ntask:\n" + str(task))
#             
#             #Mark non-recurrent tasks for removal
#             if task.recurrence_pattern is None:
#                 dead_tasks.append(itask)
#             #Compute new due time for recurrent tasks
#             else:
#                 task.due_time = self.compute_next_due_time(
#                             datetime.utcnow(), task.recurrence_pattern, True)
# 
#         #Remove dead (non recurrent) tasks, after they have been executed.
#         dead_tasks.reverse()
#         for itask in dead_tasks:
#             del self.data.tasks[itask]    
#     
#     
#     def create_final_update_tasks(self):
#         """
#         Create tasks that update the listing information shortly after the 
#         auctions end. We want to know the final price of each auction.
#         20 auctions are updated at once.
#         """
#         logging.info("Creating update tasks, to get final prices.")
#         if len(self.data.listings) == 0:
#             return
# 
#         #Create administration information if it doesn't exist
#         try:
#             self.data.listings["final_update_pending"]
#         except KeyError:
#             self.data.listings["final_update_pending"] = 0.0
#         
#         #Get listings where final price is unknown and 
#         #    where no final update is pending.
#         #Note! Three-valued logic: 1., 0., nan
#         where_no_final = ((self.data.listings["final_price"] != True) &
#                           (self.data.listings["final_update_pending"] != True))
#         no_final = self.data.listings[where_no_final]
#         no_final = no_final.sort("time")
#         if len(no_final) == 0:
#             return
#         
#         #group listings into groups of 20 (max for Ebay get-items request)
#         n_group = 20
#         elem_nums = list(range(len(no_final)))
#         group_nums =[int(ne / n_group) for ne in elem_nums]
#         groups = no_final.groupby(group_nums)
#         
#         #Create one update task for each group
#         update_tasks = []
#         id_start = "update-"
#         for i, group in groups:
#             latest_time = group["time"].max()
#             due_time = latest_time + timedelta(minutes=30)
#             listing_ids = group["id"]
#             task = UpdateTask(id=id_start + due_time.isoformat() + "-" + str(i), 
#                               due_time=due_time, 
#                               server=None, recurrence_pattern=None, 
#                               listings=listing_ids)
# #            print task
#             update_tasks.append(task)
#             
#         self.data.add_tasks(update_tasks)
#         
#         #Remember the listings for which update tasks were just created
#         self.data.listings["final_update_pending"][where_no_final] = True
# 
# 
#     def run_daemon(self, nloops=-1):
#         """
#         Simple main loop that downloads listings.
#         To run a daemon from the command line call::
#             
#             CommandLineHandler.daemon_main()
#         
#         Parameters
#         ----------
#         nloops : int 
#             Number of cycles in the main loop. -1 means: loop infinitely.
#         """
#         #Only load listings from one month in past and one month in future
#         date_start = datetime.utcnow() - timedelta(days=30)
#         date_end = datetime.utcnow() + timedelta(days=30)
#         self.data.read_data(self.data_dir, date_start, date_end)
#         
#         self.recognizers.read_recognizers(self.data_dir)
#         self.create_final_update_tasks()
#         
#         while nloops:
#             #sleep until a task is due
#             next_due_time, sleep_secs = self.compute_next_wakeup_time()
#             logging.info("Sleeping until: {}".format(next_due_time))
#             time.sleep(sleep_secs)
# 
#             self.execute_tasks()
#             self.create_final_update_tasks()
#             self.data.write_listings()
#             self.data.write_tasks()
#             
#             nloops -= 1

