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


import math
from types import NoneType
#import time
from datetime import datetime
import dateutil.parser as dprs 
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
    
    #img_thumb ???
    #bid_count ???
    listings["title"]       = ""
    listings["description"] = ""
    listings["sold"]        = False    #successful sale if True
    listings["currency"]    = ""
    listings["price"]       = nan
    listings["shipping"]    = nan
    listings["type"]        = ""       #auction, fixed-price
    listings["time"] = datetime(1,1,1) #end time in case of auctions
    listings["location"]    = ""
    listings["country"]     = ""
    listings["condition"]   = nan      #1.: new, 0.: completely unusable
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


class EbayFindListings(object):
    """
    Find listings on Ebay. Returns only incomplete information.
    
    Uses ``findItemsByKeywords`` on the ``finding`` API:
    http://developer.ebay.com/Devzone/finding/CallRef/findItemsByKeywords.html
    """
    
    def download_xml(self, keywords, 
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
        """
        Parse the XML response from Ebay's finding API, 
        and convert it into a table of listings.
        """
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
            #bid_count???
            #successful sale
            #finished??? = itemi.sellingStatus.sellingState.text
            listings["price"][i] = itemi.sellingStatus.currentPrice.text
            listings["currency"][i] = itemi.sellingStatus.currentPrice \
                                                            .get("currencyId")
            listings["shipping"][i] = itemi.shippingInfo.shippingServiceCost \
                                                            .text
            listings["type"][i] = itemi.listingInfo.listingType.text
            listings["time"][i] = dprs.parse(itemi.listingInfo.endTime.text) 
            listings["location"][i] = itemi.location.text
            listings["country"][i] = itemi.country.text
#            listings["condition"][i] = itemi.condition.conditionId.text #TODO: convert to range 1..0
            listings["server"][i] = itemi.globalId.text
            listings["server_id"][i] = itemi.itemId.text
            listings["url_webui"][i] = itemi.viewItemURL.text
            
        #Create internal IDs - Ebay IDs are unique and do not repeat
        listings["id"] = "eb-" + listings["server_id"]
        #Put internal IDs into index
        listings.set_index("id", drop=False, inplace=True, 
                           verify_integrity=True)
        
#        print listings
        return listings
     
       
    def find(self, keywords, n_listings=10, 
             min_price=None, max_price=None, currency="EUR",
             time_from=None, time_to=None):
        """
        Find listings on Ebay by keyword.
        
        time_from, time_to: datetime in UTC
        """
        #Compute number of calls to Ebay and number of listings per call
        max_per_page = 100 #max number of listings per call - Ebay limit
        n_pages = math.ceil(n_listings / max_per_page)
        n_per_page = math.ceil(n_listings / n_pages)
        
        listings = make_listing_frame(0)
        for i_page in range(1, int(n_pages + 1)):
            xml = self.download_xml(keywords=keywords, 
                                    entries_per_page=n_per_page, 
                                    page_number=i_page, 
                                    min_price=min_price, max_price=max_price, 
                                    currency=currency, 
                                    time_from=time_from, time_to=time_to)
            listings_part = self.parse_xml(xml)
            listings = listings.combine_first(listings_part)
            
        #TODO: remove extraneous rows?
        return listings
        


class EbayGetListings(object):
    """
    Get full information on ebay listings, needs information (IDs) 
    from Ebay's finding functionality.
    """


class EbayConnector(object):
    """
    Connect to Ebay over the internet and return listings.
    
    This is the class that application code should use to connect to Ebay.
    
    Parameters
    -------------
    
    keyfile : str
        Name of the configuration file for the ``python-ebay`` library,
        that contains the (secret) access keys for the Ebay API.
        
        **Warning:** This parameter is really a global setting!
        
        If there are multiple EbayConnector instances they must all use 
        the same configuration (key) file. 
    """
    def __init__(self, keyfile):
        assert isinstance(keyfile, (str))
        eb_utils.set_config_file(keyfile)
    
    
    def find_listings(self, keywords, n_listings=10, 
                      min_price=None, max_price=None, currency="EUR",
                      time_from=None, time_to=None):
        """
        Find listings on Ebay by keyword. 
        Returns only incomplete information: the description is missing.
        
        Parameters
        -----------
        
        keywords : str
            Search string in Ebay's searching language. See:
            http://pages.ebay.com/help/search/advanced-search.html#using
        
        n_listings : int
            Number of listings that Ebay should return. Might return fewer or
            slightly more listings.
            
        min_price : float
            Minimum price for listings, that are returned.
            
        max_price : float
            Maximum price for listings, that are returned.
            
        currency : str
            Currency unit for ``min_price`` and ``max_price``.
        
        time_from : datetime
            Earliest end time for listings (auctions) that are returned.
            Time is in UTC!
            
        time_to : datetime
            Latest end time for listings (auctions) that are returned.
            Time is in UTC!
        """
        assert isinstance(keywords,  (str))
        assert isinstance(n_listings,(int))
        assert isinstance(min_price, (float, int, NoneType))
        assert isinstance(max_price, (float, int, NoneType))
        assert isinstance(time_from, (datetime, NoneType))
        assert isinstance(time_to,   (datetime, NoneType))
        
        f = EbayFindListings()
        listings = f.find(keywords, n_listings, min_price, max_price, currency, 
                          time_from, time_to)
        return listings
    
    
    def update_listings(self, listings):
        pass
