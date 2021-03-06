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
Get listings from Ebay through its API.
"""

import os.path
import math
import json
import logging
from datetime import datetime
from pprint import pformat

import pandas as pd
from ebaysdk.finding import Connection as FConnection
from ebaysdk.shopping import Connection as SConnection
import ebaysdk.exception
import requests.exceptions

from libclair.dataframes import make_data_frame
from libclair.textprocessing import HtmlTool
from econdata.models import Listing



class EbayError(Exception):
    pass


def to_str_list(list_or_str):
    """
    Convert list of strings to long comma separated string.
    A single string is returned unaltered.
    """
    if isinstance(list_or_str, str):
        return list_or_str
    elif isinstance(list_or_str, list):
        return ', '.join(list_or_str)
    else:
        raise TypeError('Expecting list or str.')



class EbayFindingAPIConnector(object):
    """
    Abstraction for Ebay's finding API. 
    
    Connects to Ebay over the internet and returns listings.
    Can search with keywords and can return new listings. 
    However it can't get all information, especially not the item's description.
    
    Application code should **not** use this class, but rather ``EbayConnector``.
    
    Relevant Ebay documentation here:
    
    http://developer.ebay.com/DevZone/finding/CallRef/index.html
    
    Parameters
    -------------
    
    keyfile : str
        Name of the configuration file for the ``python-ebay`` library,
        that contains the (secret) access keys for the Ebay API.

    ebay_site : str
        Ebay site (country) where the search is executed. 
        
        * Ebay USA: 'EBAY-US'
        * Ebay Germany: 'EBAY-DE'
    
        http://developer.ebay.com/Devzone/finding/Concepts/SiteIDToGlobalID.html
        
    ebay_name : str
        String that will be put into the ``df['site']`` field of the dataframe. 
        For example ``'ebay'``.
    """
    def __init__(self, keyfile, ebay_site, ebay_name):
        assert isinstance(keyfile, (str, type(None)))
        assert os.path.isfile(keyfile) 
        assert isinstance(ebay_site, str)
        assert isinstance(ebay_name, str)

        self.keyfile = keyfile
        self.ebay_site = ebay_site
        self.ebay_name = ebay_name

    def find_listings(self, keywords, n_listings, 
                      price_min=None, price_max=None, currency="USD",
                      time_from=None, time_to=None):
        """
        Find listings on Ebay by keyword. 
        Returns only incomplete information: the description is missing.
        
        Calls the Ebay API function 'findItemsAdvanced':
        
        https://developer.ebay.com/devzone/finding/CallRef/findItemsAdvanced.html

        Parameters
        -----------
        
        keywords : str
            Search string in Ebay's searching language. See:
            http://pages.ebay.com/help/search/advanced-search.html#using
        
        n_listings : int
            Number of listings that Ebay should return. Might return fewer or
            slightly more listings.
            
            Currently limited to 100 listings, the maximum number of listings 
            in one page.
            
        price_min : float
            Minimum price for listings, that are returned.
            
        price_max : float
            Maximum price for listings, that are returned.
            
        currency : str
            Currency unit for ``price_min`` and ``price_max``.
            
            US Dollar: USD
            Euro: EUR
            
            https://developer.ebay.com/devzone/finding/CallRef/Enums/currencyIdList.html
        
        time_from : datetime
            Earliest end time for listings (auctions) that are returned.
            Time is in UTC!
            
        time_to : datetime
            Latest end time for listings (auctions) that are returned.
            Time is in UTC!
        
        Returns
        -------
        
        pandas.DataFrame
            Table with one row for each listing. Our Id is the index.
            
            Some columns are empty (especially "description"), because Ebay's
            find API call doesn't return this information. These columns 
            can be filled in with a subsequent call to ``update_listings``.
        """
        assert isinstance(keywords, (str))
        assert isinstance(n_listings, (int))
        assert isinstance(price_min, (float, int, type(None)))
        assert isinstance(price_max, (float, int, type(None)))
        assert isinstance(currency,  (str, type(None)))
        assert isinstance(time_from, (datetime, pd.Timestamp, type(None)))
        assert isinstance(time_to,   (datetime, pd.Timestamp, type(None)))

        # Ebay returns a maximum of 100 listings per call (pagination).
        # Compute necessary number of calls to Ebay and number of 
        # listings per call. 
        max_per_page = 100  # max number of listings per call - Ebay limit
        n_pages = math.ceil(n_listings / max_per_page)
        n_per_page = round(n_listings / n_pages)
        
        # Call Ebay repeatedly and concatenate results
        listings = make_data_frame(Listing, 0)
        for i_page in range(1, int(n_pages + 1)):
            resp = self._call_find_api(keywords, n_per_page, i_page,
                                        price_min, price_max, currency, 
                                        time_from, time_to)
            listings_part = self._parse_find_response(resp)
            # Stop searching when Ebay returns an empty result.
            if len(listings_part) == 0:
                break
            listings = listings.append(listings_part, ignore_index=True,
                                       verify_integrity=False)

        return listings

    def _call_find_api(self, keywords, n_per_page, i_page,
                        price_min=None, price_max=None, currency="USD",
                        time_from=None, time_to=None):
        """
        Perform Ebay API call to find listings on Ebay; by keyword. 
        Returns only incomplete information: the description is missing.
        
        For documentation on parameters see: ``EbayConnector.find_listings``

        * Calls the Ebay API function 'findItemsAdvanced':
            https://developer.ebay.com/devzone/finding/CallRef/findItemsAdvanced.html

        * Ebay's searching language. 
            http://pages.ebay.com/help/search/advanced-search.html#using
        
        * Currency unit for ``price_min`` and ``price_max``.
            * US Dollar: USD
            * Euro: EUR
            
            https://developer.ebay.com/devzone/finding/CallRef/Enums/currencyIdList.html
        """
        itemFilters = []
        if price_min:
            itemFilters += [{'name': 'MinPrice', 'value': price_min, 
                             'paramName': 'Currency', 'paramValue': currency}]
        if price_max:
            itemFilters += [{'name': 'MaxPrice', 'value': price_max, 
                             'paramName': 'Currency', 'paramValue': currency}]
        if time_from:
            itemFilters += [{'name': 'EndTimeFrom', 
                             'value': time_from.strftime("%Y-%m-%dT%H:%M:%S.000Z")}]
        if time_to:
            itemFilters += [{'name': 'EndTimeTo', 
                             'value': time_to.strftime("%Y-%m-%dT%H:%M:%S.000Z")}]
        try:
            api = FConnection(config_file=self.keyfile, siteid=self.ebay_site)
            response = api.execute('findItemsAdvanced', 
                                   {'keywords': keywords, 'descriptionSearch': 'true',
                                    'paginationInput': {'entriesPerPage': n_per_page,
                                                        'pageNumber': i_page},
                                    'itemFilter': itemFilters,
                                    })
        except (ebaysdk.exception.ConnectionError, 
                requests.exceptions.ConnectionError)  as err:
            err_text = 'Finding items on Ebay failed! Error: ' + str(err)
            logging.error(err_text)
            logging.debug(err.response.dict())
            raise EbayError(err_text)

#         #TODO: react on the following status information
#         # Returns the HTTP response code.
#         response_code()
#         # Returns the HTTP response status
#         response_status()
#         # Returns an array of eBay response codes
#         response_codes()

        resp_dict = response.dict()

        # Act on resonse status
        if resp_dict['ack'] == 'Success':
            logging.debug('Successfully called Ebay finding API.')
        elif resp_dict['ack'] in ['Warning', 'PartialFailure']:
            logging.warning('Ebay finding API returned warning.')
            logging.debug(pformat(resp_dict))
        else:
            logging.error('Ebay finding API returned error.')
            logging.debug(pformat(resp_dict))
            raise EbayError('Ebay finding API returned error.')
        
        return resp_dict

    def _parse_find_response(self, resp_dict):
        """
        Parse response from call to Ebay's finding API.
        
        See:
        https://developer.ebay.com/devzone/finding/CallRef/findItemsAdvanced.html#Output
        """
#         pprint(resp_dict)
        eb_items = resp_dict['searchResult']['item']
        listings = make_data_frame(Listing, len(eb_items))
        for i, item in enumerate(eb_items):
            try:
                "The ID that uniquely identifies the item listing."
                eb_id = item['itemId']
#                 print('itemId: ' + eb_id)
                listings.loc[i, 'id_site'] = eb_id
                listings.loc[i, 'title'] = item['title']
                listings.loc[i, 'item_url'] = item['viewItemURL']
                # https://developer.ebay.com/devzone/finding/CallRef/Enums/conditionIdList.html
                listings.loc[i, 'condition'] = self.convert_condition(item['condition']['conditionId'])
                listings.loc[i, 'time'] = pd.Timestamp(item['listingInfo']['endTime']).to_datetime64()
                # String describing location. For example: 'Pensacola,FL,USA'.
                listings.loc[i, 'location'] = item['location']
                # ISO currency codes. https://en.wikipedia.org/wiki/ISO_4217
                # EUR: Euro; GBP: British Pound; USD: US Dollar. 
                listings.loc[i, 'currency'] = item_currency = item['sellingStatus']['convertedCurrentPrice']['_currencyId']
                listings.loc[i, 'price'] = item['sellingStatus']['convertedCurrentPrice']['value']
                try:
                    # https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
                    # List of country codes, to which the item can be delivered. For example: 
                    # ['US', 'CA', 'GB', 'AU', 'NO'] or 'Worldwide' or 'US'.
                    listings.loc[i, 'shipping_locations'] = to_str_list(item['shippingInfo']['shipToLocations'])
                    eb_shipping_currency = item['shippingInfo']['shippingServiceCost']['_currencyId']
                    assert eb_shipping_currency == item_currency, \
                            'Prices in a listing must be of the same currency.'
                    listings.loc[i, 'shipping_price'] = item['shippingInfo']['shippingServiceCost']['value']
                except KeyError as err:
                    logging.debug('Missing field in "shippingInfo": ' + str(err))

                # https://developer.ebay.com/devzone/finding/CallRef/types/ItemFilterType.html
                listings.loc[i, 'listing_type'] = ltype = self.convert_listing_type(item['listingInfo']['listingType'])
                # https://developer.ebay.com/devzone/finding/CallRef/types/SellingStatus.html
                sstate_raw = item['sellingStatus']['sellingState']
                listings.loc[i, 'status'] = sstate = self.convert_selling_state(sstate_raw)

                if ltype in ['fixed-price', 'classified']:
                    listings.loc[i, 'is_real'] = True
                elif ltype == 'auction' and sstate == 'ended':
                    listings.loc[i, 'is_real'] = True
                else:
                    listings.loc[i, 'is_real'] = False
                
                if sstate_raw == 'EndedWithSales':
                    listings.loc[i, 'is_sold'] = True
                elif sstate_raw == 'EndedWithoutSales':
                    listings.loc[i, 'is_sold'] = False
                else:
                    listings.loc[i, 'is_sold'] = None

            except (KeyError, AssertionError) as err:
                logging.error('Error while parsing Ebay find result: ' + repr(err))
                logging.debug(pformat(item))

        listings['site'] = self.ebay_name
        return listings

    @staticmethod
    def convert_condition(ebay_condition):
        """
        Convert Ebay condition numbers to internal condition values.
        
        Ebay condition numbers:
            http://developer.ebay.com/DevZone/finding/CallRef/Enums/conditionIdList.html

        --------------------------------------------------------------
        Ebay code    Description                    Internal code
        ---------    ---------------------------    ----------------------
        1000         New, brand-new                 new
        1500         New other                      new-defects
        1750         New with defects (very small   new-defects
                     defects of clothes)
        2000         Manufacturer refurbished       refurbished
        2500         Seller refurbished             refurbished
        3000         Used                           used
        4000         Very Good (books)              used-very-good
        5000         Good (books)                   used-good
        6000         Acceptable (books)             used-acceptable
        7000         For parts or not working       not-working
        --------------------------------------------------------------

        Parameters
        ----------
        
        ebay_condition: str
            Ebay condition code (numeric string).
            
        Returns
        -------
        str
            Internal condition code.
        """
        cond_map = {'1000': 'new', '1500': 'new-defects', '1750': 'new-defects', 
                    '2000': 'refurbished', '2500': 'refurbished', 
                    '3000': 'used', 
                    '4000': 'used-very-good', '5000': 'used-good', '6000': 'used-acceptable', 
                    '7000': 'not-working', }
        return cond_map[ebay_condition]

    @staticmethod
    def convert_listing_type(listing_type):
        """
        Convert Ebay listing type (ListingType) codes to internal codes.
        
        Ebay listing type numbers:
            https://developer.ebay.com/devzone/finding/CallRef/types/ItemFilterType.html

        --------------------------------------------------------------
        Ebay code       Description                 Internal code
        ---------       ------------------------    ----------------------
        Auction         Auction listing.            auction
        AuctionWithBIN  Auction listing with        auction
                        "Buy It Now" available.
        Classified      Classified Ad.              classified
        FixedPrice      Fixed price items.          fixed-price
        StoreInventory  Store Inventory format      fixed-price
                        items.
        --------------------------------------------------------------

        Parameters
        ----------
        
        listing_type: str
            Ebay listing-type code.
            
        Returns
        -------
        str
            Internal listing-type code.
        """
        ltype_map = {'Auction': 'auction', 'AuctionWithBIN': 'auction', 
                     'Classified': 'classified', 
                     'FixedPrice': 'fixed-price', 'StoreInventory': 'fixed-price'}
        return ltype_map[listing_type]

    @staticmethod
    def convert_selling_state(selling_state):
        """
        Convert Ebay selling state codes to internal codes.
        
        Ebay selling state codes:
            https://developer.ebay.com/devzone/finding/CallRef/types/SellingStatus.html

        ---------------------------------------------------------------
        Ebay code          Description                    Internal code
        ---------          ------------------------       -------------
        Active            The listing is still live.      active
        Canceled          The listing has been canceled   canceled
                          by either the seller or eBay. 
        Ended             The listing has ended and eBay  ended
                          has completed the processing.
        EndedWithSales    The listing has been ended      ended
                          with sales. 
        EndedWithoutSales The listing has been ended      ended
                          without sales. 
        ---------------------------------------------------------------

        Parameters
        ----------
        
        selling_state: str
            Ebay selling state code.
            
        Returns
        -------
        str
            Internal selling state code.
        """
        smap = {'Active': 'active', 'Canceled': 'canceled', 'Ended': 'ended', 
                'EndedWithSales': 'ended', 'EndedWithoutSales': 'ended'}
        return smap[selling_state]
 

class EbayShoppingAPIConnector(object):
    """
    Abstraction for Ebay's shopping API. 
    
    Connect to Ebay over the internet and return listings.
    Can search with keywords and can return new listings. 
    However it can't get all information, especially not the item's description.
    
    Application code should not use this class, but rather ``EbayConnector``.
    
    http://developer.ebay.com/DevZone/shopping/docs/CallRef/index.html
    
    https://github.com/timotheus/ebaysdk-python/wiki/Shopping-API-Class
    
    Parameters
    -------------
    
    keyfile : str
        Name of the configuration file for the ``python-ebay`` library,
        that contains the (secret) access keys for the Ebay API.

    ebay_site : str
        Ebay site (country) where the search is executed. 
        
        * Ebay USA: 'EBAY-US'
        * Ebay Germany: 'EBAY-DE'
    
        http://developer.ebay.com/Devzone/finding/Concepts/SiteIDToGlobalID.html
        
    ebay_name : str
        String that will be put into the ``df['site']`` field of the dataframe. 
        For example ``'ebay'``.
    """
    def __init__(self, keyfile, ebay_site, ebay_name):
        assert isinstance(keyfile, (str, type(None)))
        assert os.path.isfile(keyfile) 
        assert isinstance(ebay_site, str)
        assert isinstance(ebay_name, str)

        self.keyfile = keyfile
        self.ebay_site = ebay_site
        self.ebay_name = ebay_name

    def update_listings(self, listings, ebay_site):
        """
        Update listings by connecting to Ebay over the Internet.
        
        Retrieves all columns in listing (as opposed to 
        ``EbayFindingAPIConnector.find_listings``.)
        
        Argument
        --------
        
        listings : pandas.DataFrame
            Table with listings that should be updated.
            Expects that column 'id' is used as the table's index.
        
        ebay_site : str
            Localized site that is accessed. Influences shipping costs and 
            currency.

        Returns
        -------
        
        pandas.DataFrame
            New table with updated information.
        """
        assert isinstance(listings, pd.DataFrame)
        assert isinstance(ebay_site, str)
        
        # Get ids from listings that are really from Ebay
        ebay_listings = listings[listings['site'] == self.ebay_name]
        ids = ebay_listings["id_site"]
        # Remove duplicate IDs
        ids = list(set(ids))
      
        # Download information in chunks of 20 listings.
        listings = make_data_frame(Listing, 0)
        for i_start in range(0, len(ids), 20):
            resp = self._call_shopping_api(ids[i_start:i_start + 20], ebay_site)
            listings_part = self._parse_shopping_response(resp)
            listings = listings.append(listings_part, ignore_index=True,
                                       verify_integrity=False)
        
        return listings

    def _call_shopping_api(self, ids, ebay_site):
        """
        Call Ebay's shopping API to get complete information about a listing. 
        """
        try:
            api = SConnection(config_file=self.keyfile, siteid=ebay_site)
            response = api.execute('GetMultipleItems', 
                                   {'IncludeSelector': 'Description,Details,ItemSpecifics,ShippingCosts',
                                    'ItemID': ids})
        except (ebaysdk.exception.ConnectionError, 
                requests.exceptions.ConnectionError) as err:
            err_text = 'Downloading full item information from Ebay failed! ' \
                       'Error: ' + str(err)
            logging.error(err_text)
            logging.debug(err.response.dict())
            raise EbayError(err_text)

#         #TODO: react on the following status information
#         # Returns the HTTP response code.
#         response_code()
#         # Returns the HTTP response status
#         response_status()
#         # Returns an array of eBay response codes
#         response_codes()

        resp_dict = response.dict()

        # Act on resonse status
        if resp_dict['Ack'] == 'Success':
            logging.debug('Successfully called Ebay shopping API.')
        elif resp_dict['Ack'] in ['Warning', 'PartialFailure']:
            logging.warning('Ebay shopping API returned warning.')
            logging.debug(pformat(resp_dict['Errors']))
        else:
            logging.error('Ebay shopping API returned error.')
            logging.debug(pformat(resp_dict))
            raise EbayError('Ebay shopping API returned error.')
        
        return resp_dict

    def _parse_shopping_response(self, resp):
        """
        Parse response from call to Ebay's shopping API.
        
        See:
        http://developer.ebay.com/DevZone/Shopping/docs/CallRef/GetMultipleItems.html
        """
#         pprint(resp)
        items = resp['Item']
        listings = make_data_frame(Listing, len(items))
        for i, item in enumerate(items):
            try:
                # ID --------------------------------------------------
                listings.loc[i, 'id_site'] = item['ItemID']
                # Product description --------------------------------------------------
                listings.loc[i, 'title'] = item['Title']
                listings.loc[i, 'description'] = HtmlTool.to_nice_text(item['Description'])
                try:
                    listings.loc[i, 'prod_spec'] = self.convert_ItemSpecifics(item['ItemSpecifics'])
                except KeyError as err:
                    logging.debug("Missing field 'ItemSpecifics': " + str(err))
                listings.loc[i, 'condition'] = self.convert_condition(item['ConditionID'])
                # Price -----------------------------------------------------------
                listings.loc[i, 'time'] = pd.Timestamp(item['EndTime']).to_datetime64()
                listings.loc[i, 'currency'] = item['ConvertedCurrentPrice']['_currencyID']
                listings.loc[i, 'price'] = item['ConvertedCurrentPrice']['value']
                try:
                    listings.loc[i, 'shipping_price'] = item['ShippingCostSummary']['ShippingServiceCost']['value']
                    shipping_currency = item['ShippingCostSummary']['ShippingServiceCost']['_currencyID']
                    assert shipping_currency == listings.loc[i, 'currency'], \
                            'Prices in a listing must be of the same currency.'
                except KeyError as err:
                    logging.debug("Missing field in 'ShippingCostSummary': " + str(err))
                # Listing Data -----------------------------------------------------------
                listings.loc[i, 'location'] = item['Location'] + ', ' + item['Country']
                listings.loc[i, 'shipping_locations'] = to_str_list(item['ShipToLocations'])
                listings.loc[i, 'seller'] = item['Seller']['UserID']
                listings.loc[i, 'item_url'] = item['ViewItemURLForNaturalSearch']
                # Status values -----------------------------------------------------------
                listings.loc[i, 'status'] = status = self.convert_listing_status_shp(item['ListingStatus'])
                listings.loc[i, 'listing_type'] = lstype = self.convert_listing_type_shp(item['ListingType'])
                quantitySold = int(item['QuantitySold'])
                
                # is_real - If True: One could really buy the item for this price.
                if lstype == 'fixed-price':
                    is_real = True
                elif lstype == 'auction' and status == 'ended' and quantitySold >= 1:
                    is_real = True
                else:
                    is_real = False
                listings.loc[i, 'is_real'] = is_real

                # is_sold - Successful sale if ``True``.
                if lstype == 'fixed-price' and quantitySold >= 1:
                    is_sold = True
                elif lstype == 'auction' and status == 'ended' and quantitySold >= 1:
                    is_sold = True
                else:
                    is_sold = False
                listings.loc[i, 'is_sold'] = is_sold

                if is_sold:
                    try:
                        listings.loc[i, 'buyer'] = item['HighBidder']['UserID']
                    except KeyError as err:
                        logging.debug("Missing field in 'HighBidder': " + str(err))

            except (TypeError, KeyError, AssertionError) as err:
                logging.error('Error while parsing Ebay shopping API result: ' + repr(err))
                logging.info(pformat(item))

        listings['site'] = self.ebay_name
        
        return listings

    @staticmethod
    def convert_ItemSpecifics(item_specifics):
        """Convert the ``ItemSpecifics`` to a suitable JSON representation."""
        try:
            specs = {}
            for nvpair in item_specifics['NameValueList']:
                specs[nvpair['Name']] = nvpair['Value']
        except TypeError as err:
            logging.error(str(err) + '\n`item_specifics`:\n' + pformat(item_specifics))
        
        return json.dumps(specs, ensure_ascii=False, check_circular=False, sort_keys=True)
#         return str(specs)

    @staticmethod
    def convert_condition(ebay_condition):
        """
        Convert Ebay condition numbers to internal condition values.
        
        Ebay condition numbers:
            http://developer.ebay.com/DevZone/finding/CallRef/Enums/conditionIdList.html

        --------------------------------------------------------------
        Ebay code    Description                    Internal code
        ---------    ---------------------------    ----------------------
        1000         New, brand-new                 new
        1500         New other                      new-defects
        1750         New with defects (very small   new-defects
                     defects of clothes)
        2000         Manufacturer refurbished       refurbished
        2500         Seller refurbished             refurbished
        3000         Used                           used
        4000         Very Good (books)              used-very-good
        5000         Good (books)                   used-good
        6000         Acceptable (books)             used-acceptable
        7000         For parts or not working       not-working
        --------------------------------------------------------------

        Parameters
        ----------
        
        ebay_condition: str
            Ebay condition code (numeric string).
            
        Returns
        -------
        str
            Internal condition code.
        """
        cond_map = {'1000': 'new', '1500': 'new-defects', '1750': 'new-defects', 
                    '2000': 'refurbished', '2500': 'refurbished', 
                    '3000': 'used', 
                    '4000': 'used-very-good', '5000': 'used-good', '6000': 'used-acceptable', 
                    '7000': 'not-working', }
        return cond_map[ebay_condition]

    @staticmethod
    def convert_listing_type_shp(listing_type):
        """
        Convert Ebay listing type (ListingType) codes to internal codes.
        
        Ebay listing type numbers:
            http://developer.ebay.com/DevZone/Shopping/docs/CallRef/extra/GtMltplItms.Rspns.Itm.LstngTyp.html

        ------------------------------------------------------------------------
        Ebay code         Description                              Internal code
        ----------------  ---------------------------------------  -------------
        AdType            Advertisement. Permits no bidding on     None
                          that item.
        Chinese           Single-quantity online auction format.   auction
        CustomCode        Placeholder value.                       None
        Dutch             Deprecated. Multiple-quantity online     auction
                          auction format. 
        Express           Deprecated. Germany only: eBay           None
                          Express-only format.
        FixedPriceItem    A basic fixed-price listing with a       fixed-price
                          Quantity of 1. 
        LeadGeneration    Advertisement-style listing, no bidding  None
                          or fixed price.
        Live              Live auction, on-site auction that can   auction
                          include non-eBay bidders. 
        PersonalOffer     Second chance offer made to a non-       auction
                          winning bidder on an ended listing. 
        StoresFixedPrice  A fixed-price format for eBay Store      fixed-price
                          sellers. 
        ------------------------------------------------------------------------

        Parameters
        ----------
        
        listing_type: str
            Ebay listing-type code.
            
        Returns
        -------
        str
            Internal listing-type code.
        """
        ltype_map = {'Advertisement': None, 'Chinese': 'auction', 
                     'CustomCode': None, 'Dutch': 'auction', 'Express': None, 
                     'FixedPriceItem': 'fixed-price', 'LeadGeneration': None, 
                     'Live': 'auction', 'PersonalOffer': 'auction', 
                     'StoresFixedPrice': 'fixed-price'}
        return ltype_map[listing_type]

    @staticmethod
    def convert_listing_status_shp(listing_status):
        """
        Convert Ebay selling state codes to internal codes.
        
        Ebay listing status codes:
            http://developer.ebay.com/DevZone/Shopping/docs/CallRef/GetMultipleItems.html#Response.Item.ListingStatus
        
        ------------------------------------------------------------------------
        Ebay code         Description                              Internal code
        ----------------  ---------------------------------------  -------------
        Active            The listing is still live.               active 
        Completed         The listing has ended. You can think of  ended
                          Completed and Ended as essentially 
                          equivalent. 
        CustomCode        Placeholder value.                       None
        Ended             The listing has ended.                   ended
        ------------------------------------------------------------------------

        Parameters
        ----------
        
        listing_status: str
            Ebay selling state code.
            
        Returns
        -------
        str
            Internal selling state code.
        """
        smap = {'Active': 'active', 'Completed': 'ended', 'Ended': 'ended', 
                'CustomCode': None}
        return smap[listing_status]
 

class EbayConnector(object):
    """
    Connect to Ebay over the internet and return listings.
    
    This is the class that application code should use to connect to Ebay.
    """

    all_ebay_global_ids = {
       "EBAY-AT", "EBAY-AU", "EBAY-CH", "EBAY-DE", "EBAY-ENC", "EBAY-ES",
       "EBAY-FR", "EBAY-FRB", "EBAY-FRC", "EBAY-GB", "EBAY-HK", "EBAY-IE",
       "EBAY-IN", "EBAY-IT", "EBAY-MOT", "EBAY-MY", "EBAY-NL", "EBAY-NLB",
       "EBAY-PH", "EBAY-PL", "EBAY-SG", "EBAY-US", }
    "Legal values for Ebay's global ID."

    internal_site_name = 'ebay'
    "Value for the dataframe's 'site' field, to show that the listings come from Ebay."

    def __init__(self, keyfile):
        """
        Parameters
        -------------
        
        keyfile : str
            Name of the configuration file for the ``python-ebay`` library,
            that contains the (secret) access keys for the Ebay API.
        """
        assert isinstance(keyfile, (str, type(None)))
        assert os.path.isfile(keyfile) 

        self.keyfile = keyfile

    def find_listings(self, keywords, n_listings, ebay_site,
                      price_min=None, price_max=None, currency="USD",
                      time_from=None, time_to=None):
        """
        Find listings on Ebay by keyword. 
        Returns only incomplete information: the description is missing.
        
        Calls the Ebay API function 'findItemsAdvanced':
        
        https://developer.ebay.com/devzone/finding/CallRef/findItemsAdvanced.html

        Parameters
        -----------
        
        keywords : str
            Search string in Ebay's searching language. See:
            http://pages.ebay.com/help/search/advanced-search.html#using
        
        n_listings : int
            Number of listings that Ebay should return. Might return fewer or
            slightly more listings.
            
            Currently limited to 100 listings, the maximum number of listings 
            in one page.
            
        ebay_site : str
            Ebay site (country) where the search is executed. 
            
            * Ebay USA: 'EBAY-US'
            * Ebay Germany: 'EBAY-DE'
        
            http://developer.ebay.com/Devzone/finding/Concepts/SiteIDToGlobalID.html
        
        price_min : float
            Minimum price for listings, that are returned.
            
        price_max : float
            Maximum price for listings, that are returned.
            
        currency : str
            Currency unit for ``price_min`` and ``price_max``.
            
            US Dollar: USD
            Euro: EUR
            
            https://developer.ebay.com/devzone/finding/CallRef/Enums/currencyIdList.html
        
        time_from : datetime
            Earliest end time for listings (auctions) that are returned.
            Time is in UTC!
            
        time_to : datetime
            Latest end time for listings (auctions) that are returned.
            Time is in UTC!
        
        Returns
        -------
        
        pandas.DataFrame
            Table with one row for each listing. Our Id is the index.
            
            Some columns are empty (especially "description"), because Ebay's
            find API call doesn't return this information. These columns 
            can be filled in with a subsequent call to ``update_listings``.
        """
        assert isinstance(keywords, (str))
        assert isinstance(n_listings, (int))
        assert ebay_site in self.all_ebay_global_ids
        assert isinstance(price_min, (float, int, type(None)))
        assert isinstance(price_max, (float, int, type(None)))
        assert isinstance(currency,  (str, type(None)))
        assert isinstance(time_from, (datetime, pd.Timestamp, type(None)))
        assert isinstance(time_to,   (datetime, pd.Timestamp, type(None)))

        fapic = EbayFindingAPIConnector(self.keyfile, ebay_site, self.internal_site_name)
        listings = fapic.find_listings(keywords, n_listings, 
                                      price_min, price_max, currency, 
                                      time_from, time_to)
        self.create_ids(listings)
        # Remove duplicate rows: Ebay uses the same ID for variants of the 
        # same product.
        listings = listings.drop_duplicates(subset="id") 
        # Put internal IDs into index
        listings.set_index("id", drop=False, inplace=True,
                           verify_integrity=True)
        return listings

    def update_listings(self, listings, ebay_site):
        """
        Update listings by connecting to Ebay over the Internet.
        
        Retrieves all columns in listing (as opposed to ``find_listings``.)
        
        Argument
        --------
        
        listings : pandas.DataFrame
            Table with listings that should be updated.
            Expects that column 'id' is used as the table's index.
        
        Returns
        -------
        
        pandas.DataFrame
            New table with updated information.
        """
        assert isinstance(listings, pd.DataFrame)
        assert ebay_site in self.all_ebay_global_ids
        
        sapic = EbayShoppingAPIConnector(self.keyfile, ebay_site, 
                                         self.internal_site_name)
        listings = sapic.update_listings(listings, ebay_site)
        listings.dropna(subset=['time'], inplace=True)
        self.create_ids(listings)
        listings.drop_duplicates(['id'], keep='first', inplace=True)
        listings.set_index("id", drop=False, inplace=True,
                           verify_integrity=True)
        return listings

    def create_ids(self, listings):
        """
        Create the internal IDs for Ebay listings.
        
        The have the form: {date}-ebay-{number}
        """
        # Ebay reuses ``itemId`` values for recurrent listings of professional
        # sellers. Therefore the date is included in the listing's ID.
        dates = listings['time'].map(lambda t: t.isoformat().split('T')[0])
        listings['id'] = dates + '-' + listings['site'] + '-' + listings['id_site']
#         return listings
    
