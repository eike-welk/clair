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
from datetime import datetime
import dateutil.relativedelta
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


    def perform_tasks(self):
        """Execute the due tasks in ``self.tasks``."""
        now = datetime.utcnow()
        for key in self.tasks.keys():
            task = self.tasks[key]
            if task.due_time > now:
                continue
            print "Performing:", task.id #TODO: logging
            #Search for new listings
            if isinstance(task, SearchTask):
                lst_found = self.server.find_listings(
                                            keywords=task.query_string, 
                                            n_listings=task.n_listings, 
                                            price_min=task.price_min, 
                                            price_max=task.price_max, 
                                            currency=task.currency)
                lst_found["expected_products"].fill(task.expected_products)
                lst_found["update_time"] = datetime.utcnow()
                self.listings = lst_found.combine_first(self.listings)
            #Update known listings
            elif isinstance(task, UpdateTask):
                lst_update = self.listings.ix[task.listings]
                lst_update = self.server.update_listings(lst_update)
                lst_update["update_time"] = datetime.utcnow()
                self.listings = lst_update.combine_first(self.listings)                           
            else:
                raise TypeError("Unknown task type:" + str(type(task)) + 
                                "\ntask:\n" + str(task))
                
            #Remove tasks that are executed only once.
            if task.recurrence_pattern is None:
                del self.tasks[key]
            #TODO: Compute new due time
    
    