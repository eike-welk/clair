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
                    ListD, DictD,
                    FieldDescriptor, TableDescriptor)
FD = FieldDescriptor


LISTING_DESCRIPTOR = TableDescriptor(
    "listing_frame", "1.0", "listings",
    "2D Table of listings. "
    "Each row represents a listing on an e-commerce site.",
    [FD("id", StrD, None,
        "Internal unique ID of each listing."),
     #Training  and product recognition -----------------------------------
     FD("training_sample", BoolD, None,
        "This listing is a training sample if `True`."),
     FD("search_tasks", ListD(StrD), None,
        "List of task IDs (strings) of search tasks, "
        "that returned this listing."),
     FD("expected_products", ListD(StrD), None,
        "List of product IDs (strings)."),
     FD("products", ListD(StrD), None,
        "Products in this listing."),
     FD("products_absent", ListD(StrD), None,
        "Products not in this listing. List of product IDs (strings)."),
     #Images --------------------------------------------------------------
     FD("thumbnail", StrD, None,
        "URL of small image."),
     FD("image", StrD, None,
        "URL of large image."),
     #Product description --------------------------------------------------
     FD("title", StrD, None,
        "Short description of listing."),
     FD("description", StrD, None,
        "Long description of listing."),
     FD("prod_spec", DictD(StrD, StrD), None,
        "product specific name value pairs (dict), for example: "
        "``{'megapixel': '12'}``. The ``ItemSpecifics`` on Ebay."),
    # Status values ------------------------------------------------------
     FD("active", BoolD, None,
        "You can still buy the item if True"),
     FD("sold", BoolD, None,
        "Successful sale if ``True``."),
     FD("currency", StrD, None,
        "Currency for price EUR, USD, ..."),
     FD("price", FloatD, None,
        "Price of listing (all items together)."),
     FD("shipping", FloatD, None,
        "Shipping cost"),
     FD("type", StrD, None,
        "auction, fixed-price, unknown"),
     FD("time", DateTimeD, None,
        "Time when price is/was valid. End time in case of auctions."),
     FD("location", StrD, None,
        "Location of item (pre sale)"),
     FD("postcode", StrD, None,
        "Postal code of location"),
     FD("country", StrD, None,
        "Country of item location."),
     FD("condition", FloatD, None,
        "1.: new, 0.: completely unusable"),
     FD("seller", StrD, None,
        "User name of seller."),
     FD("buyer", StrD, None,
        "User name of buyer."),
     #Additional ----------------------------------------------------------
     FD("server", StrD, None,
        "String to identify the server."),
     FD("server_id", StrD, None,
        "ID of listing on the server."),
    #TODO: Remove? This is essentially ``not active``.
    FD("final_price", BoolD, None,
        "If True: This is the final price of the auction."),
     FD("url_webui", StrD, None,
        "Link to web representation of listing."),
     #TODO: include bid_count?
     ])


#class ListingConstants(object):
#    """
#    Name space for constants related to listing ``DataFrame``.
#    Dummy class, used by ``make_listing_frame``.
#
#    For an explanation of a listing's fields, the columns of the ``DataFrame``,
#    see the comments below.
#
#    TODO: include bid_count?
#    """
#    #List of column names
#    columns = []
#    #List of default values for each column.
#    defaults = []
#    #Dictionary {"column column":"Comment"} can be used as tool tips.
#    comments = {}
#
#    column = "id"; default = None
#    comment = "Internal unique ID of each listing."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    #Training  and product recognition -----------------------------------
#    column = "training_sample"; default = nan
#    comment = "This is training sample if `True`."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "search_tasks"; default = None
#    comment = "List of task IDs (strings) of search tasks, " \
#              "that returned this listing."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "expected_products"; default = None
#    comment = "List of product IDs (strings)."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "products"; default = None
#    comment = "Products in this listing."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "products_absent"; default = None
#    comment = "Products not in this listing. List of product IDs (strings)."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    #Images --------------------------------------------------------------
#    column = "thumbnail"; default = None
#    comment = "URL of small image."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "image"; default = None
#    comment = "URL of large image."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    #Product description --------------------------------------------------
#    column = "title"; default = None
#    comment = "Short description of listing."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "description"; default = None
#    comment = "Long description of listing."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "prod_spec"; default = None
#    comment = "product specific name value pairs (dict), for example: " \
#              "``{'megapixel': '12'}``. The ``ItemSpecifics`` on Ebay."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    # Status values ------------------------------------------------------
#    column = "active"; default = nan
#    comment = "you can still buy it if True"
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "sold"; default = nan
#    comment = "Successful sale if ``True``."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "currency"; default = None
#    comment = "Currency for price EUR, USD, ..."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "price"; default = nan
#    comment = "Price of listing (all items together)."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "shipping"; default = nan
#    comment = "Shipping cost"
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "type"; default = None
#    comment = "auction, fixed-price, unknown"
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "time"; default = None
#    comment = "Time when price is/was valid. End time in case of auctions."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "location"; default = None
#    comment = "Location of item (pre sale)"
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "postcode"; default = None
#    comment = "Postal code of location"
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "country"; default = None
#    comment = "Country of item location."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "condition"; default = nan
#    comment = "1.: new, 0.: completely unusable"
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "seller"; default = None
#    comment = "User name of seller."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "buyer"; default = None
#    comment = "User name of buyer."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    #Additional ----------------------------------------------------------
#    column = "server"; default = None
#    comment = "String to identify the server."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "server_id"; default = None
#    comment = "ID of listing on the server."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    #TODO: Remove? This is essentially ``not active``.
#    column = "final_price"; default = nan
#    comment = "If True: This is the final price of the auction."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    column = "url_webui"; default = None
#    comment = "Link to web representation of listing."
#    comments[column] = comment; columns += [column]; defaults += [default]
#
#    del column; del default; del comment



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
