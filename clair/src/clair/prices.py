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


    def compute_product_occurrence_matrix(self, listings):
        """
        Compute matrix that shows which product occurs in which listing,
        And in which condition.
        """
        matrix = None
        prices = None
        listing_ids = None
        product_ids = None
        return matrix, prices, listing_ids, product_ids
    