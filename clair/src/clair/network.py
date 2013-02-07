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

#import os
import math
from types import NoneType
from collections import defaultdict
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
    listings["id"]                = nan   #internal unique ID of each listing.
    listings["training_sample"]   = False #This is training sample if True
    listings["expected_products"] = nan   #list of product IDs
    listings["query_string"]      = nan   #String with search keywords
    
    listings["thumbnail"]   = nan          
    listings["image"]       = nan          
    
    listings["title"]       = nan
    listings["description"] = nan
    #TODO: ItemSpecifics: name value pairs eg.: {"megapixel": "12"}
    #TODO: bid_count ???
    listings["active"]      = nan  #you can still buy it if True
    listings["sold"]        = nan  #successful sale if True
    listings["currency"]    = nan  #currency for price EUR, USD, ...
    listings["price"]       = nan  #price of all items in listing
    listings["shipping"]    = nan  #shipping cost
    listings["type"]        = nan  #auction, fixed-price, unknown
    listings["time"]        = nan  #Time when price is valid. End time in case of auctions
    listings["location"]    = nan  #Location of item (pre sale)
    listings["country"]     = nan  #Country of item location
    listings["condition"]   = nan  #1.: new, 0.: completely unusable
    listings["products"]    = nan  #Products in this listing. List of DetectedProduct
    listings["server"]      = nan  #string to identify the server
    listings["server_id"]   = nan  #ID of listing on the server
#    listings["data_dir"]    = nan
    listings["url_webui"]   = nan  #Link to web representation of listing.
#    listings["server_repr"] = nan  #representation of listing on server (XML)

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
            listings["img_thumb"][i] = itemi.galleryURL
            
            listings["title"][i] = itemi.title.text
            #bid_count???
            #successful sale
            #you can still buy item if True (findItemsByKeywords only returns active listings)
            listings.set_value(i, "active", True)  
            listings["currency"][i] = itemi.sellingStatus.currentPrice \
                                                            .get("currencyId")
            listings["price"][i] = itemi.sellingStatus.currentPrice.text
            listings["shipping"][i] = itemi.shippingInfo.shippingServiceCost \
                                                            .text
            #TODO: convert to standard format: listings["type"][i] = itemi.listingInfo.listingType.text
            listings["time"][i] = dprs.parse(itemi.listingInfo.endTime.text) 
            listings["location"][i] = itemi.location.text
            listings["country"][i] = itemi.country.text
#            listings["condition"][i] = itemi.condition.conditionId.text #TODO: convert to range 1..0
            listings["server"][i] = itemi.globalId.text
            listings["server_id"][i] = itemi.itemId.text
            listings["url_webui"][i] = itemi.viewItemURL.text
            
        #Create internal IDs - Ebay IDs are unique (except for variants)
        listings["id"] = "eb-" + listings["server_id"]
#        listings.to_csv("listings0.csv")
#        print listings
        return listings
     
       
    def find(self, keywords, n_listings=10, 
             min_price=None, max_price=None, currency="EUR",
             time_from=None, time_to=None):
        """
        Find listings on Ebay by keyword.
        
        time_from, time_to: datetime in UTC
        """
        #Ebay returns a maximum of 100 listings per call (pagination).
        #Compute necessary number of calls to Ebay and number of 
        #listings per call. 
        max_per_page = 100 #max number of listings per call - Ebay limit
        n_pages = math.ceil(n_listings / max_per_page)
        n_per_page = math.ceil(n_listings / n_pages)
        
        #Call Ebay repeatedly and concatenate results
        listings = make_listing_frame(0)
        for i_page in range(1, int(n_pages + 1)):
            xml = self.download_xml(keywords=keywords, 
                                    entries_per_page=n_per_page, 
                                    page_number=i_page, 
                                    min_price=min_price, max_price=max_price, 
                                    currency=currency, 
                                    time_from=time_from, time_to=time_to)
            listings_part = self.parse_xml(xml)
            listings = listings.append(listings_part, ignore_index=True, 
                                       verify_integrity=False)

        #Remove duplicate rows: Ebay uses the same ID for variants of the 
        #same product.
        listings = listings.drop_duplicates(cols="id") 
        #Put internal IDs into index
        listings.set_index("id", drop=False, inplace=True, 
                           verify_integrity=True)
        #Store the query string
        listings["query_string"] = keywords
        return listings



class EbayGetListings(object):
    """
    Get full information on ebay listings, needs information (IDs) 
    from Ebay's finding functionality.
    """
    def download_xml(self, ids):
        """
        Call ``GetMultipleItems`` from Ebay's shopping API.
        Return the XML response.
        
        ids : list of strings
        """
        assert len(ids) <= 20 # Ebay limitation
        ids_str = ",".join(ids)
        res_xml = eb_shop.GetMultipleItems(
                    item_id=ids_str, 
                    include_selector=
                    "TextDescription,Details,ItemSpecifics,ShippingCosts", 
                    encoding="XML")
#        print res_xml
        
        return res_xml
    
        
    def parse_xml(self, xml):
        """
        Parse the XML response from Ebay's shopping API.
        """
        root = objectify.fromstring(xml)
#        print etree.tostring(root, pretty_print=True)
        if root.Ack.text != "Success":
            #TODO: logging, better error message
            raise EbayError(etree.tostring(root, pretty_print=True))
        
        item = root.Item
        nrows = len(item)
        listings = make_listing_frame(nrows)
        for i, itemi in enumerate(item):
            listings["training_sample"][i] = False #This is training sample if True
            listings["expected_products"][i] = nan #list of product IDs
            listings["query_string"][i] = nan      #String with search keywords
            
            listings["thumbnail"][i] = itemi.GalleryURL.text
            listings["image"][i] =     itemi.PictureURL.text
            
            listings["title"][i] =       itemi.Title.text 
            listings["description"][i] = itemi.Description.text
            #you can still buy item if True
            listings["active"][i] =   itemi.ListingStatus.text == "Active"
            #successful sale if True
            listings["sold"][i] =     int(itemi.QuantitySold.text) > 0
            #Currency of price: EUR, USD, ...
            listings["currency"][i] = itemi.ConvertedCurrentPrice.get("currencyID")
            listings["price"][i]    = itemi.ConvertedCurrentPrice.text
            listings["shipping"][i] = float(itemi.ShippingCostSummary.
                                            ListedShippingServiceCost)
            #Type of listing: auction, fixed-price, unknown
            l_type = defaultdict(lambda: "unknown",
                                 {"Chinese"         : "auction",
                                  "FixedPriceItem"  : "fixed-price",
                                  "StoresFixedPrice": "fixed-price" })
            listings["type"][i]      = l_type[itemi.ListingType.text]
            #Approximate time when price is/was valid, end time in case of auctions
            listings["time"][i] = dprs.parse(itemi.EndTime.text) 
            listings["location"]     = itemi.Location.text
            listings["country"]      = itemi.Country.text
            #http://developer.ebay.com/DevZone/finding/CallRef/Enums/conditionIdList.html
            #TODO: convert `ConditionID` to 0..1 listings["condition"][i] = itemi.ConditionID.text      #1.: new, 0.: completely unusable
            
            listings["server"]      = itemi.Site.text    #string to identify the server
            listings["server_id"][i] = itemi.ItemID.text #ID of item on server
#            listings["data_directory"] = ""
            listings["url_webui"] = itemi.ViewItemURLForNaturalSearch.text
#            listings["server_repr"] = nan      #representation of listing on server (XML)
        
        return listings


    def update_listings(self, listings):
        """
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
        raise Exception("Not implemented")
        pass
