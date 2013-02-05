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

from __future__ import division
from __future__ import absolute_import              


from types import NoneType
#import time
from datetime import datetime
import dateutil
from lxml import etree, objectify
import pandas as pd
from numpy import nan
import ebay.utils as eb_utils
import ebay.finding as eb_find 
import ebay.shopping as eb_shop #GetMultipleItems


def make_listing_frame(nrows):
    """
    Create a DataFrame with `nrows` listings (rows).
    
    TODO: Put into central location. 
    """
    index=[str(i) for i in range(nrows)]
    
    listings = pd.DataFrame(index=index)
    listings["id"]                = "" #internal unique ID of each listing.
    listings["training_sample"]   = False
    #list of product IDs
    listings["expected_products"] = [[] for i in range(nrows)]
    listings["query_string"]      = ""
    
    #img_thumb 
    #bid_count???
    listings["title"]       = ""
    listings["description"] = ""
    listings["sold"]        = False    #successful sale if True
    #currency???
    listings["price"]       = nan
    listings["shipping"]    = nan
    listings["type"]        = ""       #auction, fixed-price
    listings["time"] = datetime(1,1,1) #end time in case of auctions
    listings["location"]    = ""
    listings["country"]     = ""
    listings["condition"]   = nan
    #list of DetectedProduct
    listings["products"]    = [[] for i in range(nrows)]
    
    listings["server"]      = ""      #string to identify the server
    listings["server_id"]   = ""      #ID of listing on the server
#    listings["data_directory"] = ""
    listings["url_webui"]   = ""
    listings["server_repr"] = ""      #representation of listing on server (XML)

    return  listings
    

class EbayError(Exception):
    pass


class EbayFindItems(object):
    """Find listings on Ebay. Returns only incomplete information."""
    
    def call_ebay(self, keywords, 
                  entries_per_page=10, page_number=1, 
                  min_price=None, max_price=None, currency="EUR",
                  time_from=None, time_to=None):
        """
        Perform findItemsByKeywords call to Ebay over Internet.
        
        time_from, time_to: datetime in UTC
        """
        assert isinstance(time_from, (datetime, NoneType))
        assert isinstance(time_to,   (datetime, NoneType))
        
        #http://developer.ebay.com/Devzone/finding/CallRef/types/ItemFilterType.html
        item_filter = []
        if min_price:
            item_filter.append({"name":"MinPrice", "value":str(min_price), 
                                "paramName":"Currency", "paramValue":currency})
        if max_price:
            item_filter.append({"name":"MaxPrice", "value":str(max_price), 
                                "paramName":"Currency", "paramValue":currency})
        #Times in UTC
        if time_from:
            item_filter.append({"name":"EndTimeFrom", "value":
                                time_from.strftime("%Y-%m-%dT%H:%M:%S.000Z")})
        if time_to:
            item_filter.append({"name":"EndTimeTo", "value":
                                time_to.strftime("%Y-%m-%dT%H:%M:%S.000Z")})
    
        #developer.ebay.com/Devzone/finding/CallRef/findItemsByKeywords.html
        res_xml = eb_find.findItemsByKeywords(
            keywords=keywords, 
            # buyerPostalCode, 
            paginationInput= {"entriesPerPage": str(int(entries_per_page)), 
                              "pageNumber":     str(int(page_number))}, 
            sortOrder="EndTimeSoonest", 
            itemFilter = item_filter,
            # outputSelector, # SellerInfo
            encoding="XML")
#        print res_xml
        return res_xml
    
    
    def parse_xml(self, xml):
        root = objectify.fromstring(xml)
#        print etree.tostring(root, pretty_print=True)
        if root.ack.text != "Success":
            #TODO: logging, better error message
            raise EbayError(etree.tostring(root, pretty_print=True))
        
        item = root.searchResult.item
        nrows = len(item)
        listings = make_listing_frame(nrows)
        for i, itemi in enumerate(item):
            listings["title"][i] = itemi.title.text
            #img_thumb = itemi.galleryURL
            #currency???
            #bid_count???
            #successful sale
            #finished??? = itemi.sellingStatus.sellingState.text
            listings["price"][i] = itemi.sellingStatus.currentPrice.text
            listings["shipping"][i] = itemi.shippingInfo.shippingServiceCost.text
            listings["type"][i] = itemi.listingInfo.listingType.text
            listings["time"][i] = itemi.listingInfo.endTime.text
            listings["location"][i] = itemi.location.text
            listings["country"][i] = itemi.country.text
#            listings["condition"][i] = itemi.condition.conditionId.text #TODO: convert to range 1..0
            listings["server"][i] = itemi.globalId.text
            listings["server_id"][i] = itemi.itemId.text
            listings["url_webui"][i] = itemi.viewItemURL.text
            
        #Create internal IDs - Ebay IDs are unique and do not repeat
        listings["id"] = "eb-" + listings["server_id"]
        #Put internal IDs into index
        listings.set_index("id", drop=False, inplace=True, verify_integrity=True)
        
#        print listings
        return listings
        


class EbayGetItems(object):
    """
    Get full information on ebay listings, needs information (IDs) 
    from Ebay's finding functionality.
    """


class EbayConnector(object):
    """
    Connect to Ebay over the internet and return listings.
    
    WARNING
    -------
    
    parameter `keyfile` is a global setting. If there are multiple
    EbayConnector instances they must all use the same configuration (key) 
    file. 
    """
    def __init__(self, keyfile):
        eb_utils.set_config_file(keyfile)
        
    def get_listings_by_keyword(self, keywords, nmax=None, date_range=None):
        pass
    
    def update_listings(self, listings):
        pass
