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
    "Test price computation for listings with only a single product."
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



if __name__ == "__main__":
#    test_PriceEstimator_find_observed_prices()
    test_PriceEstimator_compute_product_occurrence_matrix()
    
    pass #IGNORE:W0107
