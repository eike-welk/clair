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
Text processing and machine learning.
"""

from __future__ import division
from __future__ import absolute_import              

import re 
from logging import debug, info, warning, error, critical

import lxml.html
import pandas as pd
from numpy import isnan

from clair.coredata import (SearchTask, UpdateTask, 
                            XmlSmallObjectIO, XmlBigFrameIO,
                            ProductXMLConverter, TaskXMLConverter, 
                            ListingsXMLConverter)


class DataStore(object):
    """
    Store and access the various data objects.
    
    Does disk IO, and adding objects at runtime.
    
    TODO: put into coredata, and port everything to it.
    """
    def __init__(self):
        self.data_dir = "**unknown**"
        self.tasks = {}
        self.products = {}
        self.listings = pd.DataFrame()
#        self.prices = pd.DataFrame()
    
    
    def add_products(self, products):
        """
        Add products to ``self.products``. tasks: list[product] | dict[_:product]
        """
        prod_list = products.values() if isinstance(products, dict) \
                    else products 
        for product in prod_list:
            info("Adding product: {}".format(product.id))
            self.products[product.id] = product


    def add_tasks(self, tasks):
        """Add tasks to ``self.tasks``. tasks: list[task] | dict[_:task]"""
        task_list = tasks.values() if isinstance(tasks, dict) \
                    else tasks
        for task in task_list:
            info("Adding task: {}".format(task.id))
            self.tasks[task.id] = task
    
    
    def insert_listings(self, listings):
        info("Inserting {} listings".format(len(listings)))
        self.listings = listings.combine_first(self.listings)
    
    
    def read_data(self, data_dir):
        """Read the data from disk"""
        self.data_dir = data_dir
        
        #Load products
        try:
            load_prods = XmlSmallObjectIO(self.data_dir, "products", 
                                          ProductXMLConverter())
            self.add_products(load_prods.read_data())
        except IOError, err:
            warning("Could not load product data: " + str(err))

        #Load tasks
        try:
            load_tasks = XmlSmallObjectIO(self.data_dir, "tasks", 
                                          TaskXMLConverter())
            self.add_tasks(load_tasks.read_data())
        except IOError, err:
            warning("Could not load task data: " + str(err))
            
        #Load listings
        load_listings = XmlBigFrameIO(self.data_dir, "listings", 
                                      ListingsXMLConverter())
        self.insert_listings(load_listings.read_data())
        
        #TODO: load prices
        
        self.check_consistency()
    
    
    def write_listings(self):
        io_listings = XmlBigFrameIO(self.data_dir, "listings", 
                                    ListingsXMLConverter())
        io_listings.write_data(self.listings, overwrite=True)
    
    
    def check_consistency(self):
        """
        Test if the references between the various objects are consistent.
        """
        def setn(iterable_or_none):
            if iterable_or_none is None:
                return set()
            return set(iterable_or_none)
        
        prod_ids = set(self.products.keys())
        task_ids = set(self.tasks.keys())
   
        for task in self.tasks.values():
            #Test if task contains unknown product (TODO: or server) IDs
            if isinstance(task, SearchTask):
                unk_products = setn(task.expected_products) - prod_ids
                if unk_products:    
                    warning("Unknown product ID: '{pid}', in task '{tid}'."
                            .format(pid="', '".join(unk_products), 
                                    tid=task.id))
        
        #TODO: test if ``self.listings`` contains unknown product, tasks, 
        #      or server IDs.
        for lid in self.listings.index:
            search_task = self.listings["search_task"][lid]
            if search_task not in task_ids:
                warning("Unknown task ID: '{tid}', "
                        "in listings['search_task']['{lid}']."
                        .format(tid=search_task, lid=lid))
            found_prods = setn(self.listings["expected_products"][lid])
            unk_products = found_prods - prod_ids
            if unk_products:
                warning("Unknown product ID '{pid}', "
                        "in listings['expected_products']['{lid}']."
                        .format(pid="', '".join(unk_products), lid=lid))
            found_prods = setn(self.listings["products"][lid])
            unk_products = found_prods - prod_ids
            if unk_products:
                warning("Unknown product ID '{pid}', "
                        "in listings['products']['{lid}']."
                        .format(pid="', '".join(unk_products), lid=lid))
            found_prods = setn(self.listings["products_absent"][lid])
            unk_products = found_prods - prod_ids
            if unk_products:
                warning("Unknown product ID '{pid}', "
                        "in listings['products_absent']['{lid}']."
                        .format(pid="', '".join(unk_products), lid=lid))



class HtmlTool(object):
    """Algorithms to process HTML."""
    tag = re.compile(r"<[^>]*>")
    whites = re.compile(r"[\s]+")
        
    @staticmethod
    def remove_html(html):
        """Remove tags but keep text, convert entities to Unicode characters."""
        if html is None:
            return u""
        if isinstance(html, float) and isnan(html):
            return u""
        
        text = unicode(html)
        text = HtmlTool.tag.sub("", text)
        text = HtmlTool.whites.sub(" ", text)
        #convert entities
        text = lxml.html.fromstring(text).text
        return text



class CollectText(object):
    """Extract text from listings"""
    def __init__(self):
        self.texts = pd.DataFrame()
        
        
    @staticmethod
    def to_text_dict(in_dict):
        """Convert dictionary to text. Pattern: 'key: value,'"""
        if in_dict is None:
            return u""
        if isinstance(in_dict, float) and isnan(in_dict):
            return u""
        
        text = ""
        for key, value in in_dict.iteritems():
            text += unicode(key) + ": " + unicode(value) + ", "
        return text
    
        
    def insert_listings(self, listings):
        """Extract the text from listings and store it in ``self.text``"""
        text_title = listings["title"].map(HtmlTool.remove_html)
        text_desctription = listings["description"].map(HtmlTool.remove_html)
        text_specs = listings["prod_spec"].map(self.to_text_dict)
        
        texts = pd.DataFrame(index=listings.index)
        texts["title"] = text_title
        texts["description"] = text_desctription
        texts["prod_spec"] = text_specs

        self.texts = texts.combine_first(self.texts)
        

    def insert_listings_from_files(self, data_dir):
        """Get listings from disk, and extract their text contents."""
        data = DataStore()
        data.read_data(data_dir)
        self.insert_listings(data.listings)
        
        
    def get_listings_text(self):
        """Return text for each listing separate, as Series."""
        return self.texts["title"] + self.texts["description"] + \
               self.texts["prod_spec"]


    def get_total_text(self):
        """Get text of all listings as single string"""
        return self.get_listings_text().sum()

