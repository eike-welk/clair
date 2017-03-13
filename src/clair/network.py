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


from pprint import pprint
import os.path
import math
import io
# from collections import defaultdict
import  logging
from datetime import datetime

# import dateutil.parser as dprs 
import pandas as pd
# from numpy import nan
from ebaysdk.finding import Connection as FConnection
from ebaysdk.shopping import Connection as SConnection
from ebaysdk.exception import ConnectionError

from clair.dataframes import make_listing_frame



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


def convert_ebay_condition(ebay_condition):
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


def convert_ebay_listing_type(listing_type):
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


def convert_ebay_selling_state(selling_state):
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
 

class EbayGetListings(object):
    """
    Get full information on ebay listings, needs information (IDs) 
    from Ebay's finding functionality.
    """
    @staticmethod
    def download_xml(ids):
        """
        Call ``GetMultipleItems`` from Ebay's shopping API.
        Return the XML response.
        
        ids : iterable of strings
            Iterable with Ebay IDs of items whose information is downloaded.
            Maximum length is 20. This is a limitation of Ebay.
        """
        assert len(ids) <= 20  # Ebay limitation
        ids_str = ",".join(ids)  # Create comma separated string of IDs
        res_xml = eb_shop.GetMultipleItems(
                    item_id=ids_str,
                    include_selector=
                    "Description,Details,ItemSpecifics,ShippingCosts",
                    encoding="XML")
#        print res_xml
        
        return res_xml
    
    
#     @staticmethod
#     def parse_xml(xml):
#         """
#         Parse the XML response from Ebay's shopping API.
#         
#         http://developer.ebay.com/Devzone/shopping/docs/CallRef/GetMultipleItems.html
#         """
#         root = objectify.fromstring(xml)
# #        print etree.tostring(root, pretty_print=True)
# 
#         if root.Ack.text == "Success":
#             pass
#         elif root.Ack.text in ["Warning", "PartialFailure"]:
#             error_list = [etree.tostring(err, pretty_print=True) 
#                           for err in root.Errors]
#             error_str = "\n".join(error_list)
#             logging.warning(
#                 "Ebay warning in EbayGetListings.parse_xml: " + root.Ack.text + 
#                 "\n" + error_str)
#         else:
# #            raise EbayError(etree.tostring(root, pretty_print=True))
#             logging.error("Ebay error in EbayGetListings.parse_xml: \n" + 
#                           etree.tostring(root, pretty_print=True))
#             return make_listing_frame(0)
#         
#         item = root.Item
#         nrows = len(item)
#         listings = make_listing_frame(nrows)
#         for i, itemi in enumerate(item):            
#             try: listings["thumbnail"][i] = itemi.GalleryURL.text
#             except AttributeError: pass
#             try: listings["image"][i] = itemi.PictureURL.text
#             except AttributeError: pass
#             
#             listings["title"][i] = itemi.Title.text 
#             # Escaping and un-escaping XML. Necessary for the HTML description.
#             # http://wiki.python.org/moin/EscapingXml
#             # Cleaning up html
#             # http://lxml.de/lxmlhtml.html#cleaning-up-html
#             listings["description"][i] = itemi.Description.text
#             # ItemSpecifics: 
#             try:
#                 xml_prod_specs = itemi.ItemSpecifics.NameValueList
#                 prod_specs = {}
#                 for xml_spec in xml_prod_specs:
#                     name = xml_spec.Name.text
#                     value = xml_spec.Value.text
#                     prod_specs[name] = value
#                 listings["prod_spec"][i] = prod_specs
#             except AttributeError:
#                 pass
#             # Listing status
#             # http://developer.ebay.com/Devzone/shopping/docs/CallRef/GetMultipleItems.html#Response.Item.ListingStatus
#             listings["active"][i] = itemi.ListingStatus.text == "Active"
#             listings["final_price"][i] = (itemi.ListingStatus.text in 
#                                           ["Ended", "Completed"])
#             listings["sold"][i] = int(itemi.QuantitySold.text) > 0
#             # Price and shipping cost
#             listings["currency"][i] = itemi.ConvertedCurrentPrice.get(# EUR, USD, ...
#                                                                 "currencyID")
#             listings["price"][i] = itemi.ConvertedCurrentPrice.text
#             try: listings["shipping"][i] = itemi.ShippingCostSummary \
#                                                 .ListedShippingServiceCost.text
#             except AttributeError: pass
#             # Type of listing: auction, fixed-price, unknown
#             l_type = defaultdict(lambda: "unknown",
#                                  {"Chinese"         : "auction",
#                                   "FixedPriceItem"  : "fixed-price",
#                                   "StoresFixedPrice": "fixed-price" })
#             listings["type"][i] = l_type[itemi.ListingType.text]
#             # Approximate time when price is/was valid, end time in case of auctions
#             time = dprs.parse(itemi.EndTime.text) 
#             listings["time"][i] = time.replace(tzinfo=None)
#             listings["location"][i] = itemi.Location.text
#             try: listings["postcode"][i] = itemi.PostalCode.text
#             except AttributeError: pass
#             listings["country"][i] = itemi.Country.text
#             try: listings["condition"][i] = convert_ebay_condition(# 1.: new, 0.: worthless
#                                                     itemi.ConditionID.text) 
#             except AttributeError: pass
#             listings["seller"][i] = itemi.Seller.UserID.text
#             try: listings["buyer"][i] = itemi.HighBidder.UserID.text
#             except AttributeError: pass
# #            listings["server"][i] = "Ebay-" + itemi.Site.text   #string to identify the server
#             listings["server_id"][i] = itemi.ItemID.text  # ID of item on server
# #            listings["data_directory"] = ""
#             listings["url_webui"][i] = itemi.ViewItemURLForNaturalSearch.text
# #            listings["server_repr"][i] = nan      #representation of listing on server (XML)
#         
#         # Create internal IDs - Ebay IDs are unique (except for variants)
#         listings["id"] = "eb-" + listings["server_id"]
#         
#         return listings

    @staticmethod
    def get_listings(ids):
        """
        Download detailed listings from Ebay. 
        
        Needs a ``list``, ``pandas.Series``, or any iterable of Ebay item IDs. 
        """
        eget = EbayGetListings
        
        # Remove duplicate IDs
        ids = list(set(ids))
      
        # Download information in chunks of 20 listings.
        listings = make_listing_frame(0)
        for i_start in range(0, len(ids), 20):
            xml = eget.download_xml(ids[i_start:i_start + 20])
            listings_part = eget.parse_xml(xml)
            listings = listings.append(listings_part, ignore_index=True,
                                       verify_integrity=False)
        
        # Put our IDs into index
        listings.set_index("id", drop=False, inplace=True,
                           verify_integrity=True)
        
#        #TODO: compute listings["final_price"] from ``Item.ListingStatus``
#        #      http://developer.ebay.com/Devzone/shopping/docs/CallRef/GetMultipleItems.html#Response.Item.ListingStatus
#        #Ebay shows final price some minutes after auction ends, in worst case.       
#        fp = listings["time"] < datetime.utcnow() + timedelta(minutes=15)
#        listings["final_price"] = fp

        return listings



class EbayConnector(object):
    """
    Connect to Ebay over the internet and return listings.
    
    This is the class that application code should use to connect to Ebay.
    
    Parameters
    -------------
    
    keyfile : str
        Name of the configuration file for the ``python-ebay`` library,
        that contains the (secret) access keys for the Ebay API.
    """

    EBAY_SITE_NAME = 'ebay'
    "Value for the 'site' field, to show that the listings come from Ebay."

    def __init__(self, keyfile):
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
        listings = make_listing_frame(0)
        for i_page in range(1, int(n_pages + 1)):
            resp = self._call_find_api(keywords, n_per_page, i_page, ebay_site, 
                                        price_min, price_max, currency, 
                                        time_from, time_to)
            listings_part = self._parse_find_response(resp)
            # Stop searching when Ebay returns an empty result.
            if len(listings_part) == 0:
                break
            listings = listings.append(listings_part, ignore_index=True,
                                       verify_integrity=False)

        # Remove duplicate rows: Ebay uses the same ID for variants of the 
        # same product.
        listings = listings.drop_duplicates(subset="id") 
        # Put internal IDs into index
        listings.set_index("id", drop=False, inplace=True,
                           verify_integrity=True)
        return listings

    def _call_find_api(self, keywords, n_per_page, i_page, ebay_site,
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
        
        * Ebay site (country) where the search is executed. 
            * Ebay USA: 'EBAY-US'
            * Ebay Germany: 'EBAY-DE'
        
            http://developer.ebay.com/Devzone/finding/Concepts/SiteIDToGlobalID.html
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
            api = FConnection(config_file=self.keyfile, siteid=ebay_site)
            response = api.execute('findItemsAdvanced', 
                                   {'keywords': keywords, 'descriptionSearch': 'true',
                                    'paginationInput': {'entriesPerPage': n_per_page,
                                                        'pageNumber': i_page},
                                    'itemFilter': itemFilters,
                                    })
        except ConnectionError as err:
            err_text = 'Finding items on Ebay failed! Error: ' + str(err)
            logging.error(err_text)
            logging.debug(err.response.dict())
            raise EbayError(err_text)

        resp_dict = response.dict()

        # Act on resonse status
        if resp_dict['ack'] == 'Success':
            logging.debug('Successfully called Ebay finding API.')
        elif resp_dict['ack'] in ['Warning', 'PartialFailure']:
            logging.warning('Ebay finding API returned warning.')
            sio = io.StringIO()
            pprint(resp_dict, sio)
            logging.debug(sio.getvalue())
        else:
            logging.error('Ebay finding API returned error.')
            sio = io.StringIO()
            pprint(resp_dict, sio)
            logging.debug(sio.getvalue())
            raise EbayError('Ebay finding API returned error.')
        
        return resp_dict

    def _parse_find_response(self, resp_dict):
        """
        Parse the response from the Ebay API call.
        
        See:
        https://developer.ebay.com/devzone/finding/CallRef/findItemsAdvanced.html#Output
        """
#         pprint(resp_dict)
        eb_items = resp_dict['searchResult']['item']
        listings = make_listing_frame(len(eb_items))
        for i, item in enumerate(eb_items):
            try:
                "The ID that uniquely identifies the item listing."
                eb_id = item['itemId']
#                 print('itemId: ' + eb_id)
                listings.loc[i, 'id_site'] = eb_id
                listings.loc[i, 'title'] = item['title']
                listings.loc[i, 'item_url'] = item['viewItemURL']
                
                "https://developer.ebay.com/devzone/finding/CallRef/Enums/conditionIdList.html"
                listings.loc[i, 'condition'] = convert_ebay_condition(item['condition']['conditionId'])
                
                listings.loc[i, 'time'] = pd.Timestamp(item['listingInfo']['endTime']).to_datetime64()
#                 eb_start_time = item['listingInfo']['startTime']
                
                "https://developer.ebay.com/devzone/finding/CallRef/types/ItemFilterType.html"
                ltype = convert_ebay_listing_type(item['listingInfo']['listingType'])
                listings.loc[i, 'type'] = ltype
                if ltype in ['fixed-price', 'classified']:
                    listings.loc[i, 'is_real'] = True
                else:
                    listings.loc[i, 'is_real'] = False
    
                "https://developer.ebay.com/devzone/finding/CallRef/types/SellingStatus.html"
                listings.loc[i, 'status'] = convert_ebay_selling_state(item['sellingStatus']['sellingState'])

                "String describing location. For example: 'Pensacola,FL,USA'."
                listings.loc[i, 'location'] = item['location']
                
                """
                ISO currency codes. https://en.wikipedia.org/wiki/ISO_4217
                EUR     Euro. 
                GBP     British Pound. 
                USD     US Dollar. 
                """
                eb_item_currency = item['sellingStatus']['convertedCurrentPrice']['_currencyId']
                listings.loc[i, 'currency'] = eb_item_currency
                listings.loc[i, 'price'] = item['sellingStatus']['convertedCurrentPrice']['value']

                try:
                    """
                    https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
                    List of country codes, to which the item can be delivered. For example: 
                    ['US', 'CA', 'GB', 'AU', 'NO'] or 'Worldwide' or 'US'.
                    """
                    listings.loc[i, 'shipping_locations'] = to_str_list(item['shippingInfo']['shipToLocations'])
                    
                    eb_shipping_currency = item['shippingInfo']['shippingServiceCost']['_currencyId']
                    assert eb_shipping_currency == eb_item_currency, \
                            'Prices in a listing must be of the same currency.'
        
                    listings.loc[i, 'shipping_price'] = item['shippingInfo']['shippingServiceCost']['value']
                except KeyError as err:
                    logging.debug('Missing field in "shippingInfo": ' + str(err))

            except (KeyError, AssertionError) as err:
                logging.error('Error while parsing Ebay find result: ' + repr(err))
                sio = io.StringIO()
                pprint(item, sio)
                logging.debug(sio.getvalue())

        listings['site'] = self.EBAY_SITE_NAME
        listings['is_sold'] = False

        # Ebay reuses ``itemId`` values for recurrent listings of  professional
        # sellers. Therefore the date is included in the listing's ID.
        dates = listings['time'].map(lambda t: t.isoformat().split('T')[0])
        listings['id'] = dates + '-' + listings['site'] + '-' + listings['id_site']

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
        
        ebay_listings = listings[listings['site'] == self.EBAY_SITE_NAME]
        ids = ebay_listings["id_site"]


        # Remove duplicate IDs
        ids = list(set(ids))
      
        # Download information in chunks of 20 listings.
        listings = make_listing_frame(0)
        for i_start in range(0, len(ids), 20):
            resp = self._call_update_api(ids[i_start:i_start + 20], ebay_site)
            listings_part = self._parse_update_response(resp)
            listings = listings.append(listings_part, ignore_index=True,
                                       verify_integrity=False)
        
        # Put our IDs into index
        listings.set_index("id", drop=False, inplace=True,
                           verify_integrity=True)
        return listings

    def _call_update_api(self, ids, ebay_site):
        """
        Call Ebay's shopping API to get complete information about a listing. 
        """
        print(ids)
        try:
            api = SConnection(config_file=self.keyfile, siteid=ebay_site)
#             response = api.execute('findPopularItems', {'QueryKeywords': 'Python'})
            response = api.execute('GetMultipleItems', 
                                   {'IncludeSelector': 'Description,Details,ItemSpecifics,Variations',
                                    'ItemID': ids})
        except ConnectionError as err:
            err_text = 'Updating items on Ebay failed! Error: ' + str(err)
            logging.error(err_text)
            logging.debug(err.response.dict())
            raise EbayError(err_text)

        resp_dict = response.dict()

        # Act on resonse status
        if resp_dict['Ack'] == 'Success':
            logging.debug('Successfully called Ebay finding API.')
        elif resp_dict['Ack'] in ['Warning', 'PartialFailure']:
            logging.warning('Ebay shopping API returned warning.')
            sio = io.StringIO()
            pprint(resp_dict, sio)
            logging.debug(sio.getvalue())
        else:
            logging.error('Ebay shopping API returned error.')
            sio = io.StringIO()
            pprint(resp_dict, sio)
            logging.debug(sio.getvalue())
            raise EbayError('Ebay shopping API returned error.')
        
        return resp_dict

    def _parse_update_response(self, resp):
        """
        """
        pprint(resp)
        return make_listing_frame(0)
