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
    print "finshed"



if __name__ == "__main__":
    test_PriceEstimator_find_observed_prices()
    
    pass #IGNORE:W0107
