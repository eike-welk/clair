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

import os
from os import path
from datetime import datetime, timedelta
import time
from random import randint
import logging
import argparse

import dateutil.rrule
import pandas as pd
#import numpy as np

from clair.network import EbayConnector
from clair.coredata import SearchTask, UpdateTask, DataStore
from clair.textprocessing import RecognizerController



#Configure logging to print nice messages to stderr
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime



class DaemonMain(object):
    """Main object of operation without GUI. daemon """
    def __init__(self, conf_dir, data_dir):
        self.data_dir = data_dir
        self.server = EbayConnector(path.join(conf_dir, "python-ebay.apikey"))
        self.data = DataStore()
        self.recognizers = RecognizerController()
        
    
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
            rand_max = 15 * 24 * 60 * 60 #sec - 15 days
        elif recurrence_pattern in ["w", "week", "weekly"]:
            freq = dateutil.rrule.WEEKLY
            byhour = 0
            byweekday = 0
            rand_max = 3.5 * 24 * 60 * 60 #sec - 3.5 days
        elif recurrence_pattern in ["d", "day", "daily"]:
            freq = dateutil.rrule.DAILY
            byhour = 0
            rand_max = 12 * 60 * 60 #sec - 12 hours
        elif recurrence_pattern in ["h", "hour", "hourly"]:
            freq = dateutil.rrule.HOURLY
            rand_max = 30 * 60 #sec - 30 minutes
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
    
        
    def compute_next_wakeup_time(self):
        """
        Compute time when application needs to wake up to execute next task.
        
        Lopps over all tasks in ``self.tasks``.
        
        Returns
        -------
        
        datetime, float
        
        * Time when next task is due
        * Number of seconds to sleep until the next task is due.
        """
        wakeup_time = datetime(9999, 12, 31) #The last possible month
        for task in self.data.tasks:
            wakeup_time = min(task.due_time, wakeup_time)
            
        sleep_interval = wakeup_time - datetime.utcnow()
        sleep_sec = max(sleep_interval.total_seconds(), 0.) 
        
        return wakeup_time, sleep_sec
    
    
    def execute_search_task(self, task):
        """Search for new listings. Executes a search task."""
        assert isinstance(task, SearchTask)
        
        #Get new listings from server
        lst_found = self.server.find_listings(
                                    keywords=task.query_string, 
                                    n_listings=task.n_listings, 
                                    price_min=task.price_min, 
                                    price_max=task.price_max, 
                                    currency=task.currency)
        #fill in additional information, mainly for product recognition
        lst_found["search_tasks"].fill([task.id])
        lst_found["expected_products"].fill(task.expected_products)
        lst_found["server"] = task.server
        
        #Sane handling of listings that are found by multiple search tasks.
        #Get IDs of listings that have already been found by other tasks
        common_ids = list(set(lst_found.index).intersection(
                                        set(self.data.listings.index)))
        for idx in common_ids:
            #Union of "search_tasks" list between existing and new listings
            tasks = lst_found["search_tasks"][idx] + \
                    self.data.listings["search_tasks"][idx]
            tasks = list(set(tasks))
            tasks.sort()
            lst_found["search_tasks"][idx] = tasks
            #Union of "expected_products" list between existing and new listings
            prods = lst_found["expected_products"][idx] + \
                    self.data.listings["expected_products"][idx]
            prods = list(set(prods))
            prods.sort()
            lst_found["expected_products"][idx] = prods
        
        self.data.merge_listings(lst_found)
        
        
    def execute_update_task(self, task):
        """
        Download the complete information of known listings. 
        Executes an update task.
        Tries to recognize products in updated tasks.
        """
        #Download the tasks
        lst_update = self.data.listings.ix[task.listings]
        lst_update = self.server.update_listings(lst_update)
        lst_update["server"] = task.server
#        lst_update["final_price"] = True #Use as flag, just to be sure
        self.data.merge_listings(lst_update)
        
        #Recognize products
        self.recognizers.recognize_products(lst_update.index, 
                                            self.data.listings)
        
        
    def execute_tasks(self):
        """
        Execute the due tasks in ``self.tasks``.
        
        Removes single shot tasks.
        """
        logging.info("Executing due tasks.")
        now = datetime.utcnow()
        dead_tasks = []
        for itask, task in enumerate(self.data.tasks):
            #Test is task due
            if task.due_time > now:
                continue
            
            logging.info("Executing task: {}".format(task.id))
            #Search for new listings
            if isinstance(task, SearchTask):
                self.execute_search_task(task)
            #Update known listings
            elif isinstance(task, UpdateTask):
                self.execute_update_task(task)
            else:
                raise TypeError("Unknown task type:" + str(type(task)) + 
                                "\ntask:\n" + str(task))
            
            #Mark non-recurrent tasks for removal
            if task.recurrence_pattern is None:
                dead_tasks.append(itask)
            #Compute new due time for recurrent tasks
            else:
                task.due_time = self.compute_next_due_time(
                            datetime.utcnow(), task.recurrence_pattern, True)

        #Remove dead (non recurrent) tasks, after they have been executed.
        dead_tasks.reverse()
        for itask in dead_tasks:
            del self.data.tasks[itask]    
    
    
    def create_final_update_tasks(self):
        """
        Create tasks that update the listing information shortly after the 
        auctions end. We want to know the final price of each auction.
        20 auctions are updated at once.
        """
        logging.info("Creating update tasks, to get final prices.")
        if len(self.data.listings) == 0:
            return

        #Create administration information if it doesn't exist
        try:
            self.data.listings["final_update_pending"]
        except KeyError:
            self.data.listings["final_update_pending"] = 0.0
        
        #Get listings where final price is unknown and 
        #    where no final update is pending.
        #Note! Three-valued logic: 1., 0., nan
        where_no_final = ((self.data.listings["final_price"] != True) &
                          (self.data.listings["final_update_pending"] != True))
        no_final = self.data.listings[where_no_final]
        no_final = no_final.sort("time")
        if len(no_final) == 0:
            return
        
        #group listings into groups of 20 (max for Ebay get-items request)
        n_group = 20
        elem_nums = range(len(no_final))
        group_nums =[int(ne / n_group) for ne in elem_nums]
        groups = no_final.groupby(group_nums)
        
        #Create one update task for each group
        update_tasks = []
        id_start = "update-"
        for i, group in groups:
            latest_time = group["time"].max()
            due_time = latest_time + timedelta(minutes=30)
            listing_ids = group["id"]
            task = UpdateTask(id=id_start + due_time.isoformat() + "-" + str(i), 
                              due_time=due_time, 
                              server=None, recurrence_pattern=None, 
                              listings=listing_ids)
#            print task
            update_tasks.append(task)
            
        self.data.add_tasks(update_tasks)
        
        #Remember the listings for which update tasks were just created
        self.data.listings["final_update_pending"][where_no_final] = True


    def main_download_listings(self, nloops=-1):
        """
        Simple main loop that downloads listings.
        
        Parameters
        ----------
        nloops : int 
            Number of cycles in the main loop. -1 means: loop infinitely.
        """
        #Only load listings from one month in past and one month in future
        date_start = datetime.utcnow() - timedelta(days=30)
        date_end = datetime.utcnow() + timedelta(days=30)
        self.data.read_data(self.data_dir, date_start, date_end)
        
        self.recognizers.read_recognizers(self.data_dir)
        self.create_final_update_tasks()
        
        while nloops:
            #sleep until a task is due
            next_due_time, sleep_secs = self.compute_next_wakeup_time()
            logging.info("Sleeping until: {}".format(next_due_time))
            time.sleep(sleep_secs)

            self.execute_tasks()
            self.create_final_update_tasks()
            self.data.write_listings()
            self.data.write_tasks()
            
            nloops -= 1



class CommandLineHandler(object):
    """React on the command line options of the daemon script."""
    def __init__(self):
        self.conf_dir = None
        self.data_dir = None
    
    def parse_command_line(self):
        "Parse the options, and store them in internal data."
        parser = argparse.ArgumentParser(
            description="Daemon that downloads listings from Ebay.")
        parser.add_argument("--confdir", "-c", dest="confdir",
                            help='directory for configuration files')
        parser.add_argument("--datadir", "-d", dest="datadir",
                            help='directory for data files')
        
        args = parser.parse_args()
        
        #The configuration directory defaults to the current directory
        self.conf_dir = os.getcwd()
        if args.confdir:
            self.conf_dir = args.confdir
        #The data directory defaults to the value of `confdir`.
        self.data_dir = self.conf_dir
        if args.datadir:
            self.data_dir = args.datadir
            
    
    @staticmethod
    def daemon_main():
        """
        Run the daemon: parse command line, enter main loop.
        
        Trivial runner function, that ties the deamon's components together. 
        This way all components can be tested separately, while this function
        needs no testing.
        """
        handler = CommandLineHandler()
        handler.parse_command_line()
        logging.info("Starting Clair daemon. "
                     "Configuration directory: '{c}', data directory: '{d}'."
                     .format(c=handler.conf_dir, d=handler.data_dir))
        main_loop = DaemonMain(handler.conf_dir, handler.data_dir)
        main_loop.main_download_listings()
