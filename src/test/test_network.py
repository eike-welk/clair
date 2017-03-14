# -*- coding: utf-8 -*-
###############################################################################
#    Clair - Project to discover prices on e-commerce sites.                  #
#                                                                             #
#    Copyright (C) 2013 by Eike Welk                                          #
#    eike.welk@gmx.net                                                        #
#                                                                             #
#    License: GPL                                                             #
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
Put module description here.
"""

#import pytest #contains `skip`, `fail`, `raises`, `config`

from os.path import join, dirname, abspath
# import pandas as pd

import logging
import time
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime



def relative(*paths):
    "Create file paths that are relative to the location of this file."
    return abspath(join(dirname(abspath(__file__)), *paths))



#---- EbayConnector --------------------------------------------------------- 
   
def test_EbayConnector_find_listings():
    """Test finding listings by keyword through the high level interface."""
    print('Start')
    from clair.network import EbayConnector
    
    n = 5
    ebc = EbayConnector(relative("../ebay-sdk.apikey"))
    listings = ebc.find_listings(keywords="Nikon D90", n_listings=n, 
                                 ebay_site='EBAY-US', 
                                 price_min=100, price_max=500, currency="EUR")
    
#     print(listings)
    print(listings[["title", "price", "currency", "type"]])
#     print()
    assert 0.8 * n <= len(listings) <= n #Duplicates are removed


def test_EbayConnector_update_listings():
    """Test finding listings by keyword through the high level interface."""
    from clair.network import EbayConnector
    
    n = 5
    
    c = EbayConnector(relative("../ebay-sdk.apikey"))
    listings = c.find_listings(keywords="Nikon D90", 
                               n_listings=n, ebay_site='EBAY-US',
                               price_min=100, price_max=500, currency="EUR")
#     print(listings)
#     print()
    print(listings[["title", "price", "currency", "type"]])

    #The test
    listings =c.update_listings(listings, ebay_site='EBAY-US')
    
    print()
    print(listings)
#     print()
#     print(listings[["title", "price", "currency", "type"]])

#     assert 0.95 * n <= len(listings) <= n #Duplicates are removed
    #TODO: Test that descriptions are not none
   

if __name__ == '__main__':
#     test_EbayConnector_find_listings()
    test_EbayConnector_update_listings()
    
    pass #pylint: disable=W0107
