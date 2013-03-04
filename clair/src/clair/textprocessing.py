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
import logging 
import HTMLParser

#import lxml.html
import lxml.html.clean
import pandas as pd
from numpy import isnan
import nltk

from clair.coredata import (SearchTask, UpdateTask, 
                            XmlSmallObjectIO, XmlBigFrameIO,
                            ProductXMLConverter, TaskXMLConverter, 
                            ListingsXMLConverter)


class DataStore(object):
    """
    Store and access the various data objects.
    
    Does disk IO, and adding objects at runtime.
    
    TODO: put into ``coredata`` or ``daemon_main``, and port daemon(s) to it.
    """
    def __init__(self):
        self.data_dir = ""
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
            logging.info("Adding product: {}".format(product.id))
            self.products[product.id] = product


    def add_tasks(self, tasks):
        """Add tasks to ``self.tasks``. tasks: list[task] | dict[_:task]"""
        task_list = tasks.values() if isinstance(tasks, dict) \
                    else tasks
        for task in task_list:
            logging.info("Adding task: {}".format(task.id))
            self.tasks[task.id] = task
    
    
    def insert_listings(self, listings):
        logging.info("Inserting {} listings".format(len(listings)))
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
            logging.warning("Could not load product data: " + str(err))

        #Load tasks
        try:
            load_tasks = XmlSmallObjectIO(self.data_dir, "tasks", 
                                          TaskXMLConverter())
            self.add_tasks(load_tasks.read_data())
        except IOError, err:
            logging.warning("Could not load task data: " + str(err))
            
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
        #TODO: test for unknown server IDs in SearchTask or listings.
        """
        def setn(iterable_or_none):
            if iterable_or_none is None:
                return set()
            return set(iterable_or_none)
        
        prod_ids = set(self.products.keys())
        task_ids = set(self.tasks.keys())
   
        for task in self.tasks.values():
            #Test if task contains unknown product IDs
            if isinstance(task, SearchTask):
                unk_products = setn(task.expected_products) - prod_ids
                if unk_products:    
                    logging.warning(
                            "Unknown product ID: '{pid}', in task '{tid}'."
                            .format(pid="', '".join(unk_products), 
                                    tid=task.id))
        
        #Test if ``self.listings`` contains unknown product, or task IDs.
        for lid in self.listings.index:
            search_task = self.listings["search_task"][lid]
            if search_task not in task_ids:
                logging.warning("Unknown task ID: '{tid}', "
                                "in listings['search_task']['{lid}']."
                                .format(tid=search_task, lid=lid))
            found_prods = setn(self.listings["expected_products"][lid])
            unk_products = found_prods - prod_ids
            if unk_products:
                logging.warning("Unknown product ID '{pid}', "
                                "in listings['expected_products']['{lid}']."
                                .format(pid="', '".join(unk_products), lid=lid))
            found_prods = setn(self.listings["products"][lid])
            unk_products = found_prods - prod_ids
            if unk_products:
                logging.warning("Unknown product ID '{pid}', "
                                "in listings['products']['{lid}']."
                                .format(pid="', '".join(unk_products), lid=lid))
            found_prods = setn(self.listings["products_absent"][lid])
            unk_products = found_prods - prod_ids
            if unk_products:
                logging.warning("Unknown product ID '{pid}', "
                                "in listings['products_absent']['{lid}']."
                                .format(pid="', '".join(unk_products), lid=lid))



class HtmlTool(object):
    """
    Algorithms to process HTML.
    
    TODO: HTML cleaning algorithm
    * Reduce the huge size of the descriptions
    * Keep some structure for better human readability
    """
    #Regular expressions to recognize different parts of HTML. 
    #Internal style sheets or JavaScript 
    script_sheet = re.compile(r"<(script|style).*?>.*?(</\1>)", 
                              re.IGNORECASE | re.DOTALL)
    #HTML comments - can contain ">"
    comment = re.compile(r"<!--(.*?)-->", re.DOTALL) 
    #HTML tags: <any-text>
    tag = re.compile(r"<.*?>", re.DOTALL)
    #Consecutive whitespace characters
    nwhites = re.compile(r"[\s]+")
    #For converting HTML entities to unicode
    html_parser = HTMLParser.HTMLParser()
    
    #Remove unwanted tags
    cleaner = lxml.html.clean.Cleaner(remove_unknown_tags=True,
                                      page_structure=False,
                                      style=True,
                                      remove_tags=["div", "a", "img"])
    
    
    @staticmethod
    def remove_html(html):
        """
        Remove tags but keep text, convert entities to Unicode characters.
        """
        if html is None:
            return u""
        if isinstance(html, float) and isnan(html):
            return u""
        text = HtmlTool.script_sheet.sub("", html)
        text = HtmlTool.comment.sub("", text)
        text = HtmlTool.tag.sub("", text)
        text = HtmlTool.nwhites.sub(" ", text)
        text = HtmlTool.html_parser.unescape(text)
        text = unicode(text)
        return text


    @staticmethod
    def clean_html(html):
        """
        Beautify html, remove any messy or unsafe tags.
        """
        return HtmlTool.cleaner.clean_html(html)
    
    

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
        #TODO: insert also "*products*" and "training_sample"
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

