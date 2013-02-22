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
Main module for the server and command line script.
"""

from __future__ import division
from __future__ import absolute_import              

from os import path
from datetime import datetime, timedelta
from random import randint

import dateutil.rrule
import pandas as pd

from clair.network import EbayConnector
from clair.coredata import SearchTask, UpdateTask



class MainObj(object):
    """Main object of operation without GUI. daemon """
    def __init__(self, conf_dir, data_dir):
        self.server = EbayConnector(path.join(conf_dir, "python-ebay.apikey"))
        self.tasks = {}
        self.products = {}
        self.listings = pd.DataFrame()
        self.products = pd.DataFrame()
    
    
    def add_tasks(self, tasks):
        task_list = tasks.values() if isinstance(tasks, dict) else tasks
        
        for task in task_list:
            self.tasks[task.id] = task
            
            
    def add_products(self, products):
        prod_list = products.values() if isinstance(products, dict) \
                    else products 
                    
        for product in prod_list:
            self.products[product.id] = product


    def compute_next_due_time(self, curr_time, recurrence_pattern, 
                              add_random=False):
        """
        Compute next due time for recurrent tasks.
        
        Parameters
        ----------
        
        curr_time : datetime
            Start time of the recurrence. Current time should be used.
            
        recurrence_pattern: str 
            How often should the task be executed? One of:
                * "m", "month", "monthly"
                * "w", "week", "weekly"
                * "d", "day", "daily"
                * "h", "hour", "hourly"
        
        add_random: bool
            If ``True``, add a random amount of time to the computed due time,
            to avoid load spikes. 
            If ``False``, the computed times are at the start of the interval,
            for example at 00:00 o'clock for "daily" recurrence.
            
        Returns
        -------
        datetime
            The new due time
        """
        bymonth = None; bymonthday = None; byweekday = None; byhour = None
        byminute = 0; bysecond = 0
        
        recurrence_pattern = recurrence_pattern.lower()
        if recurrence_pattern in ["m", "month", "monthly"]:
            freq = dateutil.rrule.MONTHLY
            byhour = 0
            bymonthday = 1
            rand_max = 15 * 24 * 60 * 60 #sec
        elif recurrence_pattern in ["w", "week", "weekly"]:
            freq = dateutil.rrule.WEEKLY
            byhour = 0
            byweekday = 0
            rand_max = 3.5 * 24 * 60 * 60 #sec
        elif recurrence_pattern in ["d", "day", "daily"]:
            freq = dateutil.rrule.DAILY
            byhour = 0
            rand_max = 12 * 60 * 60 #sec
        elif recurrence_pattern in ["h", "hour", "hourly"]:
            freq = dateutil.rrule.HOURLY
            rand_max = 30 * 60 #sec
        else:
            raise ValueError("Unkown recurrence_pattern: " + 
                             str(recurrence_pattern))
        
        rrule = dateutil.rrule.rrule(freq=freq, dtstart=curr_time, count=2, 
                                     bymonth=bymonth, bymonthday=bymonthday, 
                                     byweekday=byweekday, byhour=byhour, 
                                     byminute=byminute, bysecond=bysecond,
                                     cache=True)
        new_time = rrule.after(curr_time)
        
        #Add add_random component.
        if add_random:
            rand_secs = randint(0, rand_max)
            new_time += timedelta(seconds=rand_secs)
        
        return new_time
    
        
    def execute_tasks(self):
        """
        Execute the due tasks in ``self.tasks``.
        
        Removes single shot tasks.
        """
        now = datetime.utcnow()
        for key in self.tasks.keys():
            task = self.tasks[key]
            #Test is task due
            if task.due_time > now:
                continue
            
            print "Executing:", task.id #TODO: logging
            #Search for new listings
            if isinstance(task, SearchTask):
                lst_found = self.server.find_listings(
                                            keywords=task.query_string, 
                                            n_listings=task.n_listings, 
                                            price_min=task.price_min, 
                                            price_max=task.price_max, 
                                            currency=task.currency)
                lst_found["expected_products"].fill(task.expected_products)
                lst_found["server"] = task.server
                self.listings = lst_found.combine_first(self.listings)
            #Update known listings
            elif isinstance(task, UpdateTask):
                lst_update = self.listings.ix[task.listings]
                lst_update = self.server.update_listings(lst_update)
                lst_update["server"] = task.server
                self.listings = lst_update.combine_first(self.listings)                           
            else:
                raise TypeError("Unknown task type:" + str(type(task)) + 
                                "\ntask:\n" + str(task))
                
            #Remove tasks that are executed only once.
            if task.recurrence_pattern is None:
                del self.tasks[key]
            #Compute new due time for recurrent tasks
            else:
                task.due_time = self.compute_next_due_time(
                            datetime.utcnow(), task.recurrence_pattern, True)
    
    
    def create_final_update_tasks(self):
        """Create the tasks to see the final price at the end of auctions."""
        #Get listings where final price is unknown
        where_no_final = self.listings["final_price"] != True
        no_final = self.listings[where_no_final]
        no_final = no_final.sort("time")
        
        #group listings into groups of 20
        n_group = 20
        elem_nums = pd.Series(range(len(no_final)))
        group_nums = (elem_nums / n_group).apply(int)
        groups = no_final.groupby(group_nums)
        print group_nums
        print len(groups)
        
        for group in groups:
            print group
            
