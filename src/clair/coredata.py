# -*- coding: utf-8 -*-
###############################################################################
#    Clair - Project to discover prices on e-commerce sites.                  #
#                                                                             #
#    Copyright (C) 2016 by Eike Welk                                          #
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
Central data structures and basic operations on them.
"""

#import os
#import os.path as path
#import glob
##import string
#from datetime import datetime  #, timedelta
#from types import NoneType
#import random
#import logging
#
#import dateutil
#from numpy import nan, isnan  #IGNORE:E0611
#import pandas as pd
#from lxml import etree, objectify

from clair.descriptors import (
                    BoolD, StrD, IntD, FloatD, DateTimeD, 
                    ListD, # DictD,
                    FieldDescriptor as FD, TableDescriptor)


LISTING_DESCRIPTOR = TableDescriptor(
    "listing_frame", "1.0", "listings",
    "2D Table of listings. "
    "Each row represents a listing on an e-commerce site.",
    [
    # IDs ---------------------------------------------------------------------
     FD("id", StrD, None,
        "Internal unique ID of each listing."),
     FD("site", StrD, None,
        "String to identify the remote site. For example 'Ebay'."),
     FD("id_site", StrD, None,
        "ID of listing on the remote site."),
#      #Training  and product recognition 
#      # TODO: This information must go to other databases.
#      FD("training_sample", BoolD, None,
#         "This listing is a training sample if `True`."),
#      FD("search_tasks", ListD(StrD), None,
#         "List of task IDs (strings) of search tasks, "
#         "that returned this listing."),
#      FD("expected_products", ListD(StrD), None,
#         "List of product IDs (strings)."),
#      FD("products", ListD(StrD), None,
#         "Products in this listing."),
#      FD("products_absent", ListD(StrD), None,
#         "Products not in this listing. List of product IDs (strings)."),
    # Product description --------------------------------------------------
     FD("title", StrD, None,
        "Short description of listing."),
     FD("description", StrD, None,
        "Long description of listing."),
     FD("prod_spec", StrD, None,
        "Product specific name value pairs (dict), in JSON. For example: "
        "``{'megapixel': '12'}``. The ``ItemSpecifics`` on Ebay."),
     FD("condition", StrD, None,
        "Condition of the sold item(s):"
        " new, new-defects, refurbished, used,"
        " used-very-good, used-good, used-acceptable"
        " not-working"),
    # Price -----------------------------------------------------------
     FD("time", DateTimeD, None,
        "Time when price is/was valid. End time in case of auctions."),
     FD("currency", StrD, None,
        "Currency for price EUR, USD, ..."),
     FD("price", FloatD, None,
        "Price of listing (all items together)."),
     FD("shipping_price", FloatD, None,
        "Shipping cost"),
     FD("is_real", BoolD, None,
        "If True: One could really buy the item for this price. "
        "This is not a temporary price from an ongoing auction."),
     FD("is_sold", BoolD, None,
        "Successful sale if ``True``."),
    # Listing Data -----------------------------------------------------------
     FD("location", StrD, None,
        "Location of item (pre sale)"),
     FD("shipping_locations", StrD, None,
        "Locations to where the item(s) can be shipped."),
     FD("seller", StrD, None,
        "User name of seller."),
     FD("buyer", StrD, None,
        "User name of buyer."),
     FD("item_url", StrD, None,
        "Link to web representation of listing."),
    # Status values -----------------------------------------------------------
     FD("status", StrD, None,
        "State of the listing: active, canceled, ended"),
     FD("type", StrD, None,
        "Type of the listing: auction, classified, fixed-price"),
    # Additional ----------------------------------------------------------
     ])


PRICE_DESCRIPTOR = TableDescriptor(
    "price-frame", "1.0", "prices",
    "2D table of prices.",
    [FD("id", StrD, None,
        "Internal unique ID of each price."),
     FD("price", FloatD, None,
        "The numeric value of the price. For example: 'EUR', 'USD'"),
     FD("currency", StrD, None,
        "The currency of the price."),
     FD("condition", FloatD, None,
        "Multiplier for condition. \n"
        "1.0: new/perfect, 0.7: used, 0.0: worthless. "),
     FD("time", DateTimeD, None,
        "Time and date at which the price was payed."),
     FD("product", StrD, None,
        "ID of product for which the price is recorded."),
     FD("listing", StrD, None,
        "ID of listing from which the price is taken"),
     FD("type", StrD, None,
        """
        Type of the price record. The types are:

        'observed'
            There was a listing containing only one product, and this was
            the price.
        'estimated'
            The price was determined from listings with multiple products,
            with some mathematical algorithm.
        'average'
            This is an average price.
        'guessed'
            A human has guessed the price.
        'notsold'
            Item was not sold at this price.
        """),
     FD("avg_period", StrD, None,
        "Time span for taking average. Can be 'day', 'week', 'month'."),
     FD("avg_num_listings", IntD, None,
        "Number of listings used in computation of average."),
     ])


PRODUCT_DESCRIPTOR = TableDescriptor(
    "product-frame", "1.0", "products",
    "2D table of products.",
    [FD("id", StrD, None,
        "Internal unique ID of each product."),
     FD("name", StrD, None,
        "Product name. A single line of text."),
     FD("important_words", ListD(StrD), None,
        "<p>Important patterns for the text recognition algorithms.</p>"
        "<p>Each line is one pattern. The patterns can contain spaces.</p>"),
     FD("categories", ListD(StrD), None,
        "Categories for grouping products. Each line is one category."),
     FD("description", StrD, None,
        "Description of the product. Any text."),
     ])


SEARCH_TASK_DESCRIPTOR = TableDescriptor(
    "search-task-frame", "1.0", "search-tasks",
    "Tasks to search for a certain product.",
    [FD("id", StrD, None,
        "Internal unique ID of each product."),
     FD("due_time", DateTimeD, None,
        "Time when task should be executed for the next time."),
     FD("server", StrD, None,
        "The server where products should be searched."),
     FD("recurrence_pattern", StrD, None,
        "How frequently should the task be executed."),
     FD("query_string", StrD, None,
        "The query string that is given to the server."),
     FD("n_listings", IntD, None,
        "Number of listings that should be returned by the server."),
     FD("price_min", FloatD, None,
        "Minimum price for searched items."),
     FD("price_max", FloatD, None,
        "Maximum price for searched items."),
     FD("currency", StrD, None,
        "Currency of the prices."),
     FD("expected_products", ListD(StrD), None,
        "<p>IDs of products that are expected in listings found by this "
        "search.</p>"
        "<p>The product identification algorithm searches only for "
        "products in this list. Each line is one product.</p>"),
     ])


UPDATE_TASK_DESCRIPTOR = TableDescriptor(
    "update-task-frame", "1.0", "update-tasks",
    "Tasks to update the information for certain listings.",
    [FD("id", StrD, None,
        "Internal unique ID of each product."),
     FD("due_time", DateTimeD, None,
        "Time when task should be executed for the next time."),
     FD("server", StrD, None,
        "Server on which the listings are located."),
     FD("recurrence_pattern", StrD, None,
        "How frequently should the task be executed."),
     FD("listings", ListD(StrD), None,
        "List of listing IDs. The listings that should be updated."),
     ])
