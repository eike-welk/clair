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
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
from numpy import NaN, newaxis

from clair.coredata import make_price_frame, make_price_id


class PriceEstimator(object):
    """
    Estimate product prices from listings.
    
    TODO: Convert some of the frequently used function arguments into 
          object attributes.
        
    TODO: Special price objects for listings that were not sold.
    """
    def __init__(self):
        self.default_currency = "EUR"
        self.default_condition = 0.7 #used, very good condition
        self.average_mid_time = datetime(2000, 1, 15)
        self.avg_period = "week"
    
    def find_observed_prices(self, listings_frame):
        """
        Search listings_frame with only one product, and create prices from them.
        These prices are called 'observed' prices here.
        """
        #Price data is first collected in list of dicts, that is later 
        #converted to a ``DataFrame``. Each dict is a row of the ``DataFrame``.
        price_data = []
        for _, listing in listings_frame.iterrows():
            #Select sold listings with only one product
            curr_prods = listing["products"]
            if len(curr_prods) != 1:
                continue
            if listing["sold"] != 1.:
                continue
            #Put the price data into dict
            single_price_data = {}
            single_price_data["price"] = listing["price"]
            single_price_data["currency"] = listing["currency"]
            single_price_data["condition"] = listing["condition"]
            single_price_data["time"] = listing["time"]
            single_price_data["product"] = curr_prods[0]
            single_price_data["listing"] = listing["id"]
            single_price_data["type"] = "observed"
            single_price_data["avg_period"] = "none"
            single_price_data["avg_num_listings"] = 1
            single_price_data["id"] = make_price_id(single_price_data)
            price_data.append(single_price_data)

        price_frame = pd.DataFrame(price_data)
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
        assert len(listings) > 0, "listings must not be empty"
        
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
                logging.debug("Unknown product(s) {u}. Listing ID: {i}."
                              .format(u=set(curr_prods) - products, i=idx))
                continue
            if len(curr_prods) == 0:
                continue
            if listing["sold"] != 1.:
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
        #Produce dummy product names for testing
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
    
    
    def solve_prices_lstsq(self, matrix, listing_prices, 
                           listing_ids, product_ids):
        """
        Compute average product prices. 
        Uses linear least square algorithm.
        """
        #Assert correct shapes of all matrices and vectors.
        assert len(matrix.shape) == 2, "matrix must be 2D array"
        assert matrix.shape[0] > 0, "matrix must not be empty"
        assert matrix.shape[1] > 0, "matrix must not be empty"
        assert len(listing_prices.shape) == 1, "listing_prices must be 1D array"
        assert len(product_ids.shape) == 1, "product_ids must be 1D array"
        assert matrix.shape[0] == listing_prices.shape[0], \
               "Each row of `matrix` is one listing. Each listing needs a price."
        assert matrix.shape[1] == product_ids.shape[0], \
               "Each column of `matrix` represents one product." \
               "Each product need an ID"
        assert listing_prices.shape == listing_ids.shape, \
               "Each listing needs a (unique) ID."
        
        logging.debug("Solving linear least problem. Matrix shape: ({r}, {c})"
                      .format(r=matrix.shape[0], c=matrix.shape[1]))
        
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
        #If matrix rank is too low to compute all prices, find problematic 
        #columns. These column are zero or collinear. 
        #The associated prices are later excluded from the result.
        if rank < matrix.shape[1]:
            logging.info("Rank deficient matrix. Rank: {}. Should have: {}."
                         .format(rank, matrix.shape[1]))
            good_rows, good_cols, problem_products = \
                self.find_problems_rank_deficient_matrix(matrix, product_ids)
#            product_prices[~good_cols] = NaN
        else:
            good_rows = np.ones(matrix.shape[0], dtype=bool)
            good_cols = np.ones(matrix.shape[1], dtype=bool)
            problem_products = []
        
        #TODO: loop for removal of outliers by weighting them low 
        #      http://en.wikipedia.org/wiki/Outlier
        #      One method may be an adaption of Cook's Distance:
        #      * Try to remove rows that have large errors one by one. 
        #      * If the estimated values change much after the row is removed,
        #        then this row is an outlier. 
        #      http://en.wikipedia.org/wiki/Cook%27s_distance
        return product_prices, good_rows, good_cols, problem_products
        
        
    def create_prices_lstsq_soln(self, matrix, 
                                 listing_prices, listing_ids,
                                 product_prices, product_ids,
                                 good_rows, good_cols, listings=None):
        """
        Create product prices from the results of the linear least 
        square algorithm.

        Parameters
        ----------
        matrix : np.array[float]
            System matrix of linear least square problem. Each row represents 
            one listing. each column represents one product. Each entry
            represents the condition of a product in a listing. Conditions
            range from 1...0.; 1: new, 0.7: used, 0: unusable.
            
        listing_prices : np.array[float]
            Prices of listings, constant (known) term of equation system
            
        listing_ids : np.array[basestring]
            Listing ID of each matrix's row.
        
        product_prices : np.array[float]
            Average price of each product. The solution of the equation system.
        
        product_ids : np.array[basestring]
            IDs of the products, represented by elements of `product_prices`
            and columns of `matrix`.
        
        good_cols : np.array[bool]
            Where `True` prices could be computed by least square algorithm.
        
        good_rows : np.array[bool]
            Where `True` listings contain only products whose prices could be
            computed by the solution algorithm. 
        
        listings : pd.DataFrame
            The listings from which the the system of equations was generated.
            Will usually contain additional listings.
            
        Returns
        -------
        prices : pd.DataFrame
            The computed prices as a `pd.DataFrame`.
        """
        assert matrix.shape[0] == len(listing_prices) == len(listing_ids)
        assert matrix.shape[1] == len(product_prices) == len(product_ids)
        
        good_prod_idxs = np.argwhere(good_cols)[:, 0]
        
        #Create the average prices
        #Price data is first collected in list of dicts, that is later 
        #converted to a ``DataFrame``. Each dict is a row of the ``DataFrame``.
        prices = make_price_frame(0)
        price_data = []
        for iprod in range(len(product_prices)):
            if iprod not in good_prod_idxs:
                continue
            single_price_data = {}
            #Multiply with condition, solver returns prices for condition "new".
            single_price_data["price"] = \
                            product_prices[iprod] * self.default_condition
            single_price_data["currency"] = self.default_currency
            single_price_data["condition"] = self.default_condition
            single_price_data["time"] = self.average_mid_time
            single_price_data["product"] = product_ids[iprod]
            single_price_data["listing"] = u"{}-average".format(
                                                        self.average_mid_time)
            single_price_data["type"] = "average"
            single_price_data["avg_period"] = self.avg_period
            #Get number of listings that were used for this average price, from 
            #the system matrix. Count non-zero entries in the price's column. 
            prod_col = matrix[:, iprod]
            prod_col = np.where(prod_col > 0, 1, 0) #Don't count NaNs
            n_listings = np.sum(prod_col)
            single_price_data["avg_num_listings"] = n_listings
            single_price_data["id"] = make_price_id(single_price_data)
            price_data.append(single_price_data)
        
        avg_prices = pd.DataFrame(price_data)
        prices = prices.append(
                        avg_prices, ignore_index=True, verify_integrity=False)
        
        #Create prices for each item of each listing 
        #Protect against prices that are NaN
        good_prod_prices = np.where(np.isnan(product_prices), 
                                    0, product_prices)
        #Price data is first collected in list of dicts. Each dict is a price.
        price_data = []
        for ilist in range(len(listing_prices)):
            #Each row of `matrix` represents a listing
            row = matrix[ilist, :]
            
            #compute percentage of each product on total listing price 
            #from average prices.
            virt_prod_prices = row * good_prod_prices
            list_prod_percent = virt_prod_prices / virt_prod_prices.sum()
            #compute price of each item in listing based on these percentages
            listing_price = listing_prices[ilist]
            list_prod_prices = list_prod_percent * listing_price
            
            #`listings` data frame can be `None` for more easy testing.
            if listings is not None:
                list_id = listing_ids[ilist]
                list_currency = listings.ix[list_id, "currency"]
                list_time = listings.ix[list_id, "time"]
            else:
                list_id = listing_ids[ilist]
                list_currency = "Unknown Currency"
                list_time = datetime(2000, 1, 1)
            prod_idxs = np.argwhere(row > 0)[:, 0]
            if len(prod_idxs) == 1:
                price_type = "observed"
                avg_period = "none"
            else:
                price_type = "estimated"
                avg_period = self.avg_period
            
            #Create a price record for each of the estimated product prices
            for iprod in prod_idxs:
                if iprod not in good_prod_idxs:
                    continue
                single_price_data = {}
                single_price_data["price"] = list_prod_prices[iprod]
                single_price_data["currency"] = list_currency
                single_price_data["condition"] = row[iprod]
                single_price_data["time"] = list_time
                single_price_data["product"] = product_ids[iprod]
                single_price_data["listing"] = list_id
                single_price_data["type"] = price_type
                single_price_data["avg_period"] = avg_period
                #TODO: Better algorithm, analogous to algorithm above for average prices.
                single_price_data["avg_num_listings"] = len(listing_prices)
                single_price_data["id"] = make_price_id(single_price_data)
                price_data.append(single_price_data)
        
        list_prices = pd.DataFrame(price_data)
        prices = prices.append(
                        list_prices, ignore_index=True, verify_integrity=False)
        prices.set_index("id", drop=False, inplace=True, verify_integrity=True)
        return prices
    
    
    def compute_prices(self, listings, products,
                       time_start=None, time_end=None, 
                       avg_period="week"):
        """
        Compute prices from listings. 
        
        Uses linear least square method to compute prices of items that are
        sold together with other items. This is equivalent to averaging, to
        prices over the listings that were used to compute the prices.
        
        TODO: Delete old prices.
        """
        logging.info("Starting to compute prices...")
        
        if avg_period == "week":
            offset = pd.datetools.Week(weekday=0)
            self.avg_period = "week"
        else:
            raise NotImplementedError()
        
        #If no start- or end-points are given start or end of listing sequence
        #Include listings in incomplete periods at start and end of sequence.
        if time_start is None:
            time_start = listings["time"].min()
            time_start = offset.rollback(time_start)
        if time_end is None:
            time_end = listings["time"].max()
            time_end = offset.rollforward(time_end)
        
        #Create start and end of desired intervals.
        intervals = pd.date_range(time_start, time_end, freq=offset)
        prices = make_price_frame(0)

        #Create list of product IDs. Exclude the place holders the have 
        #names"xxx-unknown" starting with
        product_ids = [p.id for p in products 
                       if not p.id.startswith("xxx-unknown")]
        if len(product_ids) == 0:
            logging.error("Empty product list.")
            return prices
        
        #Chop listings into intervals and loop over them.
        listings = listings.sort("time")
        for i in range(len(intervals) - 1):
            intv_start = intervals[i]
            intv_end = intervals[i + 1]
            
            offset_mid = timedelta(
                            seconds=(intv_end - intv_start).total_seconds() / 2)
            self.average_mid_time = intv_start + offset_mid
            
            intv_listings = listings.ix[(listings["time"] >= intervals[i]) &
                                        (listings["time"] < intervals[i + 1])]
            logging.debug("Interval start: {s}, end: {e}, n listings: {n}."
                          .format(s=intervals[i], e=intervals[i + 1],
                                  n=len(intv_listings)))
            if len(intv_listings) == 0:
                continue
            
            matrix, listing_prices, listing_ids, product_ids = \
                self.compute_product_occurrence_matrix(
                                                    intv_listings, product_ids)
            if matrix.shape[0] == 0:
                logging.debug("No valid listing prices.")
                continue
            product_prices, good_rows, good_cols, problem_products = \
                self.solve_prices_lstsq(
                            matrix, listing_prices, listing_ids, product_ids)
            intv_prices = self.create_prices_lstsq_soln(
                                        matrix, listing_prices, listing_ids, 
                                        product_prices, product_ids, 
                                        good_rows, good_cols, listings)
            prices = prices.append(intv_prices)
            
        return prices
    