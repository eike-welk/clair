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
Price estimation algorithms.
"""

from __future__ import division
from __future__ import absolute_import              

import logging

import numpy as np
from numpy import nan

from clair.coredata import make_price_frame, create_price_id


class PriceEstimator(object):
    """Estimate product prices from listings."""
    
    def find_observed_prices(self, listings_frame):
        """
        Search listings_frame with only one product, and create prices from them.
        These prices are called 'observed' prices here.
        """
        ids, prices, currencies, conditions = [], [], [], []
        times, products, listings = [], [], []
        for _, listing in listings_frame.iterrows():
            #Select listings with only one product
            curr_prods = listing["products"]
            if len(curr_prods) != 1:
                continue
            #Put the price data into lists
            prod = curr_prods[0]
            time = listing["time"]
            ids.append(create_price_id(time, prod))
            prices.append(listing["price"])
            currencies.append(listing["currency"])
            conditions.append(listing["condition"])
            times.append(time)
            products.append(prod)
            listings.append(listing["id"])
                
        price_frame = make_price_frame(len(prices))
        price_frame["id"] = ids
        price_frame["price"] = prices
        price_frame["currency"] = currencies
        price_frame["condition"] = conditions
        price_frame["time"] = times
        price_frame["product"] = products
        price_frame["listing"] = listings
        price_frame["type"] = "observed"
        price_frame.set_index("id", drop=False, inplace=True, 
                              verify_integrity=True)
        
        return price_frame


    def compute_product_occurrence_matrix(self, listings, product_ids):
        """
        Compute matrix that shows which product occurs in which listing,
        And in which condition.
        
        The matrix and the related vectors are used to compute the average 
        prices for products with a linear least square method. The following
        over determined equation must be solved::
            
            matrix * pp = prices
            
        Where ``pp`` is the unknown vector of product prices.
        
        Returns
        -------
        matrix : np.array [float]
            Array that records which product is present in which listing.
             
            shape = (number listings, number products)
            
            Each row represents a listing, each column represents a product.
            An item in a listing is represented by a number between 0. and 1.,
            its "condition". 1 means *new*; 0.7 used; 0.1 broken.  
             
        prices : np.array [float]
            Vector of known listing prices.
        
        listing_ids : np.array [basestring]
            Listing IDs, corresponds with `prices` and rows of `matrix`.
        
        product_ids : np.array [basestring]
            Product IDs, corresponds with columns of `matrix` (and the unknown
            product vector).
        """
        products = set(product_ids)
        prod_list = list(products)
        prod_list.sort()
        prod_inds = dict(zip(prod_list, range(len(prod_list))))
        
        matrix = np.zeros((len(listings), len(products)))
        prices = np.empty(len(listings))
        prices.fill(nan)
        listing_ids = np.empty(len(listings), dtype=object)
        listing_ids.fill(None)
        product_ids = np.array(prod_list, dtype=object)
        
        for il, (idx, listing) in enumerate(listings.iterrows()):
            curr_prods = listing["products"]
            if curr_prods is None:
                logging.error("Undefined field 'products'. Listing ID: {}."
                              .format(idx))
                continue
            if not products.issuperset(curr_prods):
                logging.error("Unknown product(s) {u}. Listing ID: {i}."
                              .format(u=set(curr_prods) - products, i=idx))
                continue
            if len(curr_prods) == 0:
                continue
            prices[il] = listing["price"]
            listing_ids[il] = idx
            curr_condition = listing["condition"]
            for prod in curr_prods:
                ip = prod_inds[prod]
                matrix[il, ip] = curr_condition
                
        valid = ~(np.isnan(prices) | (listing_ids == None))
        matrix = matrix[valid, :]
        prices = prices[valid]
        listing_ids = listing_ids[valid]        
        
        return matrix, prices, listing_ids, product_ids
    