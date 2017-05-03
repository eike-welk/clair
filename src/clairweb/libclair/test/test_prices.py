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
            
#import pytest #contains `skip`, `fail`, `raises`, `config` 

import time
import os.path as path

import numpy as np
from numpy import array, dot, abs #sqrt, sum
from numpy.linalg import norm
import matplotlib.pylab as pl

#Set up logging fore useful debug output, and time stamps in UTC.
import logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime



def relative(*path_comps):
    "Create file path_comps that are relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_comps))


def test_PriceEstimator_find_observed_prices():
    "Test price computation for listings with only a single product."
    from clair.coredata import DataStore
    from clair.prices import PriceEstimator
    print "start"
    
    data = DataStore()
    data.read_data(relative("../../example-data"))
    
    test_listings = data.listings.ix[0:20]
    print test_listings
    
    estimator = PriceEstimator()
    prices = estimator.find_observed_prices(test_listings)
    
    print prices.to_string()
    #TODO: assertions
    print "finshed"


def test_PriceEstimator_compute_product_occurrence_matrix():
    "Test construction of matrix for linear least square algorithm."
    from clair.coredata import DataStore
    from clair.prices import PriceEstimator
    print "start"
    
    data = DataStore()
    data.read_data(relative("../../example-data"))
    
    test_listings = data.listings.ix[0:20]
    print test_listings
    print test_listings.to_string(columns=["products", "price"])
    product_ids = [u'nikon-d70', u'nikon-d90', u'nikon-sb-24', u'nikon-sb-26', 
                   u'nikon-18-70-f/3.5-4.5--1', u'nikon-18-105-f/3.5-5.6--1',
                   u'nikon-28-85-f/3.5-4.5--1']
    
    estimator = PriceEstimator()
    matrix, prices, listing_ids, product_ids = \
        estimator.compute_product_occurrence_matrix(test_listings, product_ids)
    
    print
    print "matrix:\n", matrix
    print "matrix rank:", np.linalg.matrix_rank(matrix)
    print "number products:", len(product_ids)
    print "prices:\n", prices
    print "listing_ids:\n", listing_ids
    print "product_ids:\n", product_ids
    
    
    #TODO: assertions
    print "finshed"


def test_PriceEstimator_solve_prices_lstsq_1():
    "Test linear least square algorithm with real data."
    from clair.coredata import DataStore
    from clair.prices import PriceEstimator
    print "start"
    
    data = DataStore()
    data.read_data(relative("../../example-data"))
    
    #Take a small amount of test data.
    listings = data.listings.ix[0:50]
#    listings = data.listings
#    product_ids = [p.id for p in data.products]
    product_ids = [u'nikon-d70', u'nikon-d90', u'nikon-sb-24', u'nikon-sb-26', 
                   u'nikon-18-70-f/3.5-4.5--1', u'nikon-18-105-f/3.5-5.6--1',
                   u'nikon-28-85-f/3.5-4.5--1']
    print listings
    print listings.to_string(columns=["products", "price"])
    
    estimator = PriceEstimator()
    
    #Create matrix and vectors for linear least square
    matrix, listing_prices, listing_ids, product_ids = \
        estimator.compute_product_occurrence_matrix(listings, product_ids)
    print
    print "matrix:\n", matrix
    print "matrix rank:", np.linalg.matrix_rank(matrix)
    print "number products:", len(product_ids)
    print "listing_prices:\n", listing_prices
    print "listing_ids:\n", listing_ids
    print "product_ids:\n", product_ids
    
    product_prices, good_rows, good_cols, problem_products = \
                estimator.solve_prices_lstsq(matrix, listing_prices, 
                                                     listing_ids, product_ids)
    
    print "product_prices:\n", product_prices * 0.7
    #TODO: assertions
    print "finshed"


def test_PriceEstimator_solve_prices_lstsq_2():
    "Test linear least square algorithm with artificial data."
    from clair.prices import PriceEstimator
    
    def print_vals():
        print "matrix:\n", matrix
        print "matrix rank:", np.linalg.matrix_rank(matrix)
        print "number products:", len(product_ids)
        print "listing_prices:\n", listing_prices
        print "listing_ids:\n", listing_ids
        print "product_ids:\n", product_ids
        print "product_prices:\n", product_prices
        print "real_prices:\n", real_prices
        print "good_rows:\n", good_rows
        print "good_cols:\n", good_cols
        print "problem_products:\n", problem_products
        
    print "start"
    
    estimator = PriceEstimator()
    
    #Listing IDs, unimportant in this test.
    listing_ids = array(["l1", "l2", "l3", "l4", "l5", 
                        "l6", "l7", "l8", "l9", "l10"])
    
    #Product IDs, and "real" prices for checking errors
    product_ids = array(["a", "b", "c", "d", "e"])
    real_prices = array([500, 200, 100, 50.,  5.])
    
    print "Matrix has full rank, no noise ---------------------------------"
    #Matrix that represents the listings, each row is a listing
    matrix =     array([[ 1.,  0.,  0.,  0.,  0.,],
                        [ 1.,  0.,  0.,  0.,  0.,],
                        [ 0.,  1.,  0.,  0.,  0.,],
                        [ 0.,  1.,  0.,  0.,  0.,],
                        [ 1.,  1.,  0.,  0.,  0.,],
                        [ 1.,  0.,  1.,  0.,  0.,],
                        [ 0.,  0.,  1.,  1.,  0.,],
                        [ 0.,  0.,  1.,  0.,  1.,],
                        [ 0.,  0.,  0.,  1.,  1.,],
                        [ 1.,  1.,  1.,  1.,  1.,],
                        ])
    #compute listing prices from the real prices
    listing_prices = dot(matrix, real_prices)
    #Compute the product prices
    product_prices, good_rows, good_cols, problem_products = \
                estimator.solve_prices_lstsq(matrix, listing_prices, 
                                                     listing_ids, product_ids)
    
    print_vals()
    np.testing.assert_allclose(product_prices, real_prices)
    
    print "\nMatrix has full rank, with noise --------------------------------"
    #compute listing prices with noise
    listing_prices = dot(matrix, real_prices)
    listing_prices += np.random.normal(0, 0.1, (10,)) * listing_prices
    #Compute the product prices
    product_prices, good_rows, good_cols, problem_products = \
                estimator.solve_prices_lstsq(matrix, listing_prices, 
                                                     listing_ids, product_ids)
    print_vals()
    
    err_norm = norm(product_prices - real_prices)
    print "Error norm:", err_norm
    res_good = np.asarray(abs(product_prices - real_prices) 
                          < real_prices * 0.2, dtype=int)
    print "Number of results exact to 20%:", sum(res_good)
    #This test might occasionally fail because current noise is too large.
    assert sum(res_good) >= 3
    
    print "\nMatrix has insufficient rank, no noise ---------------------------------"
    #Matrix that represents the listings, each row is a listing
    matrix =     array([[ 1.,  0.,  0.,  0.,  0.,],
                        [ 1.,  0.,  0.,  0.,  0.,],
                        [ 0.,  1.,  0.,  0.,  0.,],
                        [ 0.,  1.,  0.,  0.,  0.,],
                        [ 1.,  1.,  0.,  0.,  0.,],
                        [ 1.,  0.,  1.,  0.,  0.,],
                        [ 0.,  0.,  0.,  1.,  1.,],
                        [ 0.,  0.,  0.,  1.,  1.,],
                        [ 0.,  0.,  0.,  1.,  1.,],
                        [ 1.,  1.,  1.,  0.,  0.,], 
                        ])
    #compute listing prices from the real prices
    listing_prices = dot(matrix, real_prices)
    #Compute the product prices
    product_prices, good_rows, good_cols, problem_products = \
                estimator.solve_prices_lstsq(matrix, listing_prices, 
                                                     listing_ids, product_ids)
    print_vals()
    np.testing.assert_allclose(product_prices[0:3], real_prices[0:3])
    
    print "\nMatrix has insufficient rank, no noise  ---------------------------------"
    #Pathological case for the current algorithm
    matrix = array([[ 1.,  0.,  0.,  1.,  1.,],
                    [ 0.,  1.,  0.,  1.,  1.,],
                    [ 0.,  0.,  1.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,], ])
    #compute listing prices from the real prices
    listing_prices = dot(matrix, real_prices)
    #Compute the product prices
    product_prices, good_rows, good_cols, problem_products = \
                estimator.solve_prices_lstsq(matrix, listing_prices, 
                                                     listing_ids, product_ids)
    print_vals()
    np.testing.assert_allclose(product_prices[0:3], real_prices[0:3])
    
    print "Matrix is 1*2 ------------------------"
    #Listing IDs, unimportant in this test.
    listing_ids = array(["l1"])
    
    #Product IDs, and "real" prices for checking errors
    product_ids = array(["a", "b"])
    real_prices = array([500, 200.])
    
    #Matrix that represents the listings, each row is a listing
    matrix =     array([[0.7, 0]])
    #compute listing prices from the real prices
    listing_prices = dot(matrix, real_prices)
    #Compute the product prices
    product_prices, good_rows, good_cols, problem_products = \
                estimator.solve_prices_lstsq(matrix, listing_prices, 
                                                     listing_ids, product_ids)
    
    print_vals()
    np.testing.assert_allclose(product_prices[good_cols], 
                               real_prices[good_cols])

    print "Matrix is 1*1 (but has full rank, no noise) ------------------------"
    #Listing IDs, unimportant in this test.
    listing_ids = array(["l1"])
    
    #Product IDs, and "real" prices for checking errors
    product_ids = array(["a"])
    real_prices = array([500])
    
    #Matrix that represents the listings, each row is a listing
    matrix =     array([[0.7]])
    #compute listing prices from the real prices
    listing_prices = dot(matrix, real_prices)
    #Compute the product prices
    product_prices, good_rows, good_cols, problem_products = \
                estimator.solve_prices_lstsq(matrix, listing_prices, 
                                                     listing_ids, product_ids)
    
    print_vals()
    np.testing.assert_allclose(product_prices[good_cols], 
                               real_prices[good_cols])

    print "finshed"


def test_PriceEstimator_find_problems_rank_deficient_matrix():
    "Test linear least square algorithm with artificial data."
    from clair.prices import PriceEstimator
    
    def print_all():
#        print "matrix_new:\n", matrix_new
        print "good_rows:", good_rows
        print "good_cols:", good_cols
        print "problem_products:", problem_products
    
    estimator = PriceEstimator()
    
    print "Matrix has full rank ---------------------------------"
    #Matrix that represents the listings, each row is a listing
    matrix = array([[ 1.,  0.,  0.,  0.,  0.,],
                    [ 1.,  0.,  0.,  0.,  0.,],
                    [ 0.,  1.,  0.,  0.,  0.,],
                    [ 0.,  1.,  0.,  0.,  0.,],
                    [ 1.,  1.,  0.,  0.,  0.,],
                    [ 1.,  0.,  1.,  0.,  0.,],
                    [ 0.,  0.,  1.,  1.,  0.,],
                    [ 0.,  0.,  1.,  0.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 1.,  1.,  1.,  1.,  1.,], 
                    ])
    good_rows, good_cols, problem_products = \
                        estimator.find_problems_rank_deficient_matrix(matrix)
    print_all()
    assert all(good_cols == [True, True, True, True, True])
    assert problem_products == []
    
    print "\nMatrix has insufficient rank ---------------------------------"
    matrix = array([[ 1.,  0.,  0.,  0.,  0.,],
                    [ 1.,  0.,  0.,  0.,  0.,],
                    [ 0.,  1.,  0.,  0.,  0.,],
                    [ 0.,  1.,  0.,  0.,  0.,],
                    [ 1.,  1.,  0.,  0.,  0.,],
                    [ 1.,  0.,  1.,  0.,  0.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 1.,  1.,  1.,  0.,  0.,], 
                    ])
    good_rows, good_cols, problem_products = \
                        estimator.find_problems_rank_deficient_matrix(matrix)
    print_all()
    assert all(good_cols == [True, True, True, False, False])
    assert problem_products == ["3", "4"]
    
    print "\nMatrix has insufficient rank, pathological case ----------------"
    #Pathological case for the current algorithm
    matrix = array([[ 1.,  0.,  0.,  1.,  1.,],
                    [ 0.,  1.,  0.,  1.,  1.,],
                    [ 0.,  0.,  1.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,],
                    [ 0.,  0.,  0.,  1.,  1.,], 
                    ])
    good_rows, good_cols, problem_products = \
                        estimator.find_problems_rank_deficient_matrix(matrix)
    print_all()
    assert all(good_cols == [True, True, True, False, False])
    assert problem_products == ["3", "4"]


    print "\nPathological case shape = (1, 2) ----------------"
    #Pathological case for the current algorithm
    matrix = array([[ 0.7,  0.]])
    good_rows, good_cols, problem_products = \
                        estimator.find_problems_rank_deficient_matrix(matrix)
    print_all()
    assert all(good_cols == [True, False])
    assert problem_products == ["1"]


def test_PriceEstimator_create_prices_lstsq_soln_1():
    "Test creation of price records with real data."
    from clair.coredata import DataStore
    from clair.prices import PriceEstimator
    print "start"
    
    data = DataStore()
    data.read_data(relative("../../example-data"))
    
    #Use all data as test data
#    listings = data.listings
    product_ids = [p.id for p in data.products 
                   if not p.id.startswith("xxx-unknown")]
#    #Take a small amount of test data.
    listings = data.listings.ix[0:200]
#    product_ids = [u'nikon-d70', u'nikon-d90', u'nikon-sb-24', u'nikon-sb-26', 
#                   u'nikon-18-70-f/3.5-4.5--1', u'nikon-18-105-f/3.5-5.6--1',
#                   u'nikon-28-85-f/3.5-4.5--1']
    print listings
#    print listings.to_string(columns=["products", "price"])
    
    estimator = PriceEstimator()
    
    #Create matrix and vectors for linear least square
    matrix, listing_prices, listing_ids, product_ids = \
        estimator.compute_product_occurrence_matrix(listings, product_ids)
#    print
#    print "matrix:\n", matrix
#    print "matrix rank:", np.linalg.matrix_rank(matrix)
#    print "number products:", len(product_ids)
#    print "listing_prices:\n", listing_prices
#    print "listing_ids:\n", listing_ids
#    print "product_ids:\n", product_ids
    
    #Compute average product prices
    product_prices, good_rows, good_cols, problem_products = \
                estimator.solve_prices_lstsq(matrix, listing_prices, 
                                                     listing_ids, product_ids)
    
    #Create price records
    prices = estimator.create_prices_lstsq_soln(matrix, 
                                     listing_prices, listing_ids, 
                                     product_prices, product_ids,
                                     good_rows, good_cols, listings)
#    print prices.to_string()
    
    #TODO: assertions
    print "finshed"


def test_PriceEstimator_create_prices_lstsq_soln_2():
    """
    Test creation of price records from solution of linear 
    least square problem, with artificial data.
    """
    from clair.prices import PriceEstimator
    
    def print_vals():
        print "matrix:\n", matrix
        print "matrix rank:", np.linalg.matrix_rank(matrix)
        print "number products:", len(product_ids)
        print "listing_prices:\n", listing_prices
        print "listing_ids:\n", listing_ids
        print "product_ids:\n", product_ids
        print "product_prices:\n", product_prices
        print "real_prices:\n", real_prices
        
    print "start"
    
    estimator = PriceEstimator()
    
    #Listing IDs, unimportant in this test.
    listing_ids = array(["l1", "l2", "l3", "l4", "l5", 
                        "l6", "l7", "l8", "l9", "l10"])
    
    #Product IDs, and "real" prices for checking errors
    product_ids = array(["a", "b", "c", "d", "e"])
    real_prices = array([500, 200, 100, 50.,  5.])
    
    print "Matrix has full rank, no noise ---------------------------------"
    #Matrix that represents the listings, each row is a listing
    matrix =     array([[ 1.,  0.,  0.,  0.,  0.,],
                        [ 1.,  0.,  0.,  0.,  0.,],
                        [ 0.,  1.,  0.,  0.,  0.,],
                        [ 0.,  1.,  0.,  0.,  0.,],
                        [ 1.,  1.,  0.,  0.,  0.,],
                        [ 1.,  0.,  1.,  0.,  0.,],
                        [ 0.,  0.,  1.,  1.,  0.,],
                        [ 0.,  0.,  1.,  0.,  1.,],
                        [ 0.,  0.,  0.,  1.,  1.,],
                        [ 1.,  1.,  1.,  1.,  1.,],
                        ])
    #compute listing prices from the real prices
    listing_prices = dot(matrix, real_prices)
    #Compute the product prices
    product_prices, good_rows, good_cols, problem_products = \
                estimator.solve_prices_lstsq(matrix, listing_prices, 
                                             listing_ids, product_ids)
    print_vals()
    
    prices = estimator.create_prices_lstsq_soln(matrix, 
                                                listing_prices, listing_ids,
                                                product_prices, product_ids,
                                                good_cols, good_rows)
    print "prices:\n", prices.to_string()
    
    true_prices = prices["price"] / prices["condition"]
    prices_a = true_prices[prices["product"] == "a"]
    prices_b = true_prices[prices["product"] == "b"]
    prices_c = true_prices[prices["product"] == "c"]
    prices_d = true_prices[prices["product"] == "d"]
    prices_e = true_prices[prices["product"] == "e"]
    
    np.testing.assert_allclose(prices_a, 500)
    np.testing.assert_allclose(prices_b, 200)
    np.testing.assert_allclose(prices_c, 100)
    np.testing.assert_allclose(prices_d, 50)
    np.testing.assert_allclose(prices_e, 5)
        
    print "Matrix is 1*1 (but has full rank, no noise) ------------------------"
    #Listing IDs, unimportant in this test.
    listing_ids = array(["l1"])
    
    #Product IDs, and "real" prices for checking errors
    product_ids = array(["a"])
    real_prices = array([500])
    
    #Matrix that represents the listings, each row is a listing
    matrix =     array([[0.7]])
    #compute listing prices from the real prices
    listing_prices = dot(matrix, real_prices)
    #Compute the product prices
    product_prices, good_rows, good_cols, problem_products = \
                estimator.solve_prices_lstsq(matrix, listing_prices, 
                                             listing_ids, product_ids)
    print_vals()
    
    prices = estimator.create_prices_lstsq_soln(matrix, 
                                                listing_prices, listing_ids,
                                                product_prices, product_ids,
                                                good_cols, good_rows)
    print "prices:\n", prices.to_string()
    
    true_prices = prices["price"] / prices["condition"]
    prices_a = true_prices[prices["product"] == "a"]
    
    np.testing.assert_allclose(prices_a, 500)

    
def test_PriceEstimator_compute_prices_1():
    "Test main method for creation of price records with real data."
    from clair.coredata import DataStore
    from clair.prices import PriceEstimator
    print "start"
    
    data = DataStore()
    data.read_data(relative("../../example-data"))
    
    #Use all data as test data
    listings = data.listings
#    product_ids = [p.id for p in data.products 
#                   if not p.id.startswith("xxx-unknown")]
#    #Take a small amount of test data.
#    listings = data.listings.ix[0:50]
#    product_ids = [u'nikon-d70', u'nikon-d90', u'nikon-sb-24', u'nikon-sb-26', 
#                   u'nikon-18-70-f/3.5-4.5--1', u'nikon-18-105-f/3.5-5.6--1',
#                   u'nikon-28-85-f/3.5-4.5--1']
#    print listings
    print listings.to_string(columns=["products", "price"])
    
    estimator = PriceEstimator()
    prices = estimator.compute_prices(listings, data.products, 
                                      time_start=None, time_end=None, 
                                      avg_period="week")
#    print prices.to_string()
    
    prices = prices.sort("time")
    prices_d90 = prices.ix[prices["product"] == "nikon-d90"]
    pl.plot(prices_d90["time"].tolist(), prices_d90["price"].tolist())
    prices_sb26 = prices.ix[prices["product"] == "nikon-sb-26"]
    prices_sb26.set_index("time", inplace=True, verify_integrity=False)
    prices_sb26["price"].plot()
    prices_sb24 = prices.ix[prices["product"] == "nikon-sb-24"]
    prices_sb24.set_index("time", inplace=True, verify_integrity=False)
    prices_sb24["price"].plot()
    
#    pl.plot(prices_sb24["time"], prices_d90["price"])
#    pl.show()
    #TODO: assertions
    print "finshed"



if __name__ == "__main__":
#    test_PriceEstimator_find_observed_prices()
#    test_PriceEstimator_compute_product_occurrence_matrix()
#    test_PriceEstimator_solve_prices_lstsq_1()
    test_PriceEstimator_solve_prices_lstsq_2()
#    test_PriceEstimator_find_problems_rank_deficient_matrix()
#    test_PriceEstimator_create_prices_lstsq_soln_1()
#    test_PriceEstimator_create_prices_lstsq_soln_2()
#    test_PriceEstimator_compute_prices_1()
    pass #IGNORE:W0107
