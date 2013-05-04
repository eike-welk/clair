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
from numpy import NaN, newaxis

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
        listing_prices for products with a linear least square method. The following
        over determined equation must be solved::
            
            matrix * pp = listing_prices
            
        Where ``pp`` is the unknown vector of product listing_prices.
        
        Returns
        -------
        matrix : np.array [float]
            Array that records which product is present in which listing.
             
            shape = (number listings, number products)
            
            Each row represents a listing, each column represents a product.
            An item in a listing is represented by a number between 0. and 1.:
            its "condition". 1 means *new*; 0.7 used; 0.1 broken.  
             
        listing_prices : np.array [float]
            Vector of known listing listing_prices.
        
        listing_ids : np.array [basestring]
            Listing IDs, corresponds to `listing_prices` and rows of `matrix`.
        
        product_ids : np.array [basestring]
            Product IDs, corresponds to columns of `matrix` (and the unknown
            product vector).
        """
        products = set(product_ids)
        prod_list = list(products)
        prod_list.sort()
        prod_inds = dict(zip(prod_list, range(len(prod_list))))
        
        matrix = np.zeros((len(listings), len(products)))
        listing_prices = np.empty(len(listings))
        listing_prices.fill(NaN)
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
            listing_prices[il] = listing["price"]
            listing_ids[il] = idx
            curr_condition = listing["condition"]
            for prod in curr_prods:
                ip = prod_inds[prod]
                matrix[il, ip] = curr_condition
                
        valid = ~ np.isnan(listing_prices)
        matrix = matrix[valid, :]
        listing_prices = listing_prices[valid]
        listing_ids = listing_ids[valid]        
        
        return matrix, listing_prices, listing_ids, product_ids
    
    
    def find_problems_rank_deficient_matrix(self, matrix, product_ids=None):
        """
        Find problematic rows and columns in a rank deficient matrix.
        If these rows and columns are deleted the remaining matrix has full 
        rank.
        
        Returns
        -------
        matrix_new : np.array[float]
            Modified matrix 
        good_rows, good_cols : np.array[bool]
            Index arrays to access affected rows and columns
        problem_products : list[int]
            IDs of products whose prices can't be determined by linear
            least square algorithm.
        """
        n_listings, n_products = matrix.shape
        if product_ids is None:
            product_ids = [str(i) for i in range(n_products)]
        
        start_rank = np.linalg.matrix_rank(matrix)
        #Find problematic columns (products): 
        # * Add an additional row to the matrix with a single `1` 
        #   in the column that is currently tested.
        # * Compute the matrix rank.
        # * If this additional `1` increases the matrix rank, this column is 
        #   problematic. The price of its associated product can't be 
        #   determined with linear least square algorithm.
        problem_products = []
        #Vectors for fancy indexing: True for good, False for bad row/column
        good_cols = np.ones((n_products), dtype=bool)
        good_rows = np.ones((n_listings), dtype=bool)
        for i_col in range(n_products):
            addrow = np.zeros((n_products,))
            addrow[i_col] = 1
            new_mat = np.vstack((matrix, addrow))
            new_rank = np.linalg.matrix_rank(new_mat)
            if new_rank > start_rank:
                problem_products.append(product_ids[i_col])
                good_cols[i_col] = False
                #Problematic rows are those, where the problematic column 
                #has non zero entries.
                bad_rows = matrix[:, i_col] != 0
                good_rows = good_rows & (~bad_rows)
                logging.debug("Product {p} (column {c}) is problematic "
                              "for price estimation."
                              .format(p=product_ids[i_col], c=i_col))
                
        return good_rows, good_cols, problem_products
    
    
    def compute_avg_product_prices(self, matrix, listing_prices, 
                                   listing_ids, product_ids):
        """
        Compute average product prices. 
        Uses linear least square algorithm.
        """
        #Assert correct shapes of all matrices and vectors.
        assert len(matrix.shape) == 2, "matrix must be 2D array"
        assert len(listing_prices.shape) == 1, "listing_prices must be 1D array"
        assert len(product_ids.shape) == 1, "product_ids must be 1D array"
        assert matrix.shape[0] == listing_prices.shape[0], \
               "Each row of `matrix` is one listing. Each listing needs a price."
        assert matrix.shape[1] == product_ids.shape[0], \
               "Each column of `matrix` represents one product." \
               "Each product need an ID"
        assert listing_prices.shape == listing_ids.shape, \
               "Each listing needs a (unique) ID."
        
        #TODO: maybe also scale prices so that they are nearly 1. would require
        #      two iterations. Idea::
        #          A * x = b
        #      Introduce diagonal matrix `S` so that all components of the 
        #      unknown vector become approximately 1. The scale matrix is 
        #      determined from a previous attempt to solve the system of 
        #      equations. ::
        #          x = S * x1 (with x1 ~=~ [1, 1, ..., 1])
        #          A * x = (A * S) * x1 = b 
        #      Does the matrix become numerically problematic by this algorithm?
        #      Does this have any positive effect at all?
         
        #Scale rows, so that `listing_prices` become 1. But no division by 0!
        # This decreases the influence of expensive products and listings.
        # Otherwise cheap products have bigger errors (in percent) than 
        # expensive products.
        # This algorithm effectively assigns low weights to expensive listings.
        scale_facts = 1/np.maximum(listing_prices, 0.01)
        listing_prices_s = listing_prices * scale_facts
        matrix_s = matrix * scale_facts[:, newaxis]
        #Compute least square solution to equation system
        product_prices, _resid, rank, _sing_vals = np.linalg.lstsq(
                                                    matrix_s, listing_prices_s)
        #If matrix is rank deficient, find the problematic columns 
        # (zero, collinear) and exclude the associated prices from the result.
        if rank < min(matrix.shape):
            logging.info("Rank deficient matrix. Rank: {}. Should have: {}."
                         .format(rank, min(matrix.shape)))
            good_rows, good_cols, problem_products = \
                self.find_problems_rank_deficient_matrix(matrix, product_ids)
            product_prices[~good_cols] = NaN
        
        #TODO: loop for removal of outliers by weighting them low 
        #      http://en.wikipedia.org/wiki/Outlier
        #      One method may be an adaption of Cook's Distance:
        #      * Try to remove rows that have large errors one by one. 
        #      * If the estimated values change much after the row is removed,
        #        then this row is an outlier. 
        #      http://en.wikipedia.org/wiki/Cook%27s_distance
        return matrix, product_prices, listing_prices, listing_ids, product_ids
        