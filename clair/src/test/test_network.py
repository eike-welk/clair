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

import pytest #contains `skip`, `fail`, `raises`, `config`

from datetime import datetime, timedelta
from lxml import etree


#A successful response from Ebay for findItemsByKeywords
EBAY_findItemsByKeywords_RESPONSE = \
"""
<findItemsByKeywordsResponse xmlns="http://www.ebay.com/marketplace/search/v1/services">
  <ack>Success</ack>
  <version>1.12.0</version>
  <timestamp>2013-02-05T03:25:44.137Z</timestamp>
  <searchResult count="2">
    <item>
      <itemId>370730491804</itemId>
      <title>Ipod Clock Radio Dock Bad Boy Black AC NEU</title>
      <globalId>EBAY-DE</globalId>
      <primaryCategory>
        <categoryId>171949</categoryId>
        <categoryName>Sonstige</categoryName>
      </primaryCategory>
      <galleryURL>http://thumbs1.ebaystatic.com/m/mDVUZpivkdfPdyKHCY2vlxA/140.jpg</galleryURL>
      <viewItemURL>http://www.ebay.de/itm/Ipod-Clock-Radio-Dock-Bad-Boy-Black-AC-NEU-/370730491804?pt=LH_DefaultDomain_77</viewItemURL>
      <paymentMethod>CIPInCheckoutEnabled</paymentMethod>
      <paymentMethod>PayPal</paymentMethod>
      <paymentMethod>MoneyXferAccepted</paymentMethod>
      <autoPay>false</autoPay>
      <location>Gro&#223;britannien</location>
      <country>GB</country>
      <shippingInfo>
        <shippingServiceCost currencyId="EUR">0.0</shippingServiceCost>
        <shippingType>Free</shippingType>
        <shipToLocations>Worldwide</shipToLocations>
      </shippingInfo>
      <sellingStatus>
        <currentPrice currencyId="EUR">55.54</currentPrice>
        <convertedCurrentPrice currencyId="EUR">55.54</convertedCurrentPrice>
        <sellingState>Active</sellingState>
        <timeLeft>P0DT1H4M18S</timeLeft>
      </sellingStatus>
      <listingInfo>
        <bestOfferEnabled>false</bestOfferEnabled>
        <buyItNowAvailable>false</buyItNowAvailable>
        <startTime>2013-01-06T04:25:02.000Z</startTime>
        <endTime>2013-02-05T04:30:02.000Z</endTime>
        <listingType>StoreInventory</listingType>
        <gift>false</gift>
      </listingInfo>
      <condition>
        <conditionId>1000</conditionId>
        <conditionDisplayName>Neu</conditionDisplayName>
      </condition>
      <isMultiVariationListing>false</isMultiVariationListing>
      <topRatedListing>false</topRatedListing>
    </item>
    <item>
      <itemId>261163201066</itemId>
      <title>Apple iPod nano 5. Generation Orange (8 GB)</title>
      <globalId>EBAY-DE</globalId>
      <primaryCategory>
        <categoryId>73839</categoryId>
        <categoryName>iPods &amp; MP3-Player</categoryName>
      </primaryCategory>
      <galleryURL>http://thumbs3.ebaystatic.com/m/maHJnxEF0YFQ1CDq_mZhpqw/140.jpg</galleryURL>
      <viewItemURL>http://www.ebay.de/itm/Apple-iPod-nano-5-Generation-Orange-8-GB-/261163201066?pt=DE_MP3_Players</viewItemURL>
      <productId type="ReferenceID">77793916</productId>
      <paymentMethod>CIPInCheckoutEnabled</paymentMethod>
      <paymentMethod>PayPal</paymentMethod>
      <paymentMethod>MoneyXferAccepted</paymentMethod>
      <autoPay>false</autoPay>
      <postalCode>04774</postalCode>
      <location>Dahlen,Deutschland</location>
      <country>DE</country>
      <shippingInfo>
        <shippingServiceCost currencyId="EUR">5.0</shippingServiceCost>
        <shippingType>Flat</shippingType>
        <shipToLocations>DE</shipToLocations>
      </shippingInfo>
      <sellingStatus>
        <currentPrice currencyId="EUR">70.5</currentPrice>
        <convertedCurrentPrice currencyId="EUR">70.5</convertedCurrentPrice>
        <bidCount>17</bidCount>
        <sellingState>Active</sellingState>
        <timeLeft>P0DT1H31M56S</timeLeft>
      </sellingStatus>
      <listingInfo>
        <bestOfferEnabled>false</bestOfferEnabled>
        <buyItNowAvailable>false</buyItNowAvailable>
        <startTime>2013-01-31T04:57:40.000Z</startTime>
        <endTime>2013-02-05T04:57:40.000Z</endTime>
        <listingType>Auction</listingType>
        <gift>false</gift>
      </listingInfo>
      <condition>
        <conditionId>3000</conditionId>
        <conditionDisplayName>Gebraucht</conditionDisplayName>
      </condition>
      <isMultiVariationListing>false</isMultiVariationListing>
      <topRatedListing>false</topRatedListing>
    </item>
  </searchResult>
  <paginationOutput>
    <totalPages>225</totalPages>
    <totalEntries>449</totalEntries>
    <pageNumber>1</pageNumber>
    <entriesPerPage>2</entriesPerPage>
  </paginationOutput>
  <itemSearchURL>http://www.ebay.de/sch/i.html?endtimefrom=2013-02-05T03%3A35%3A43.000Z&amp;_nkw=ipod&amp;endtimeto=2013-02-07T03%3A25%3A43.000Z&amp;_LH_Time=1&amp;_ddo=1&amp;_ett=47.99971027777778&amp;_ftrt=902&amp;_ftrv=0.16637694444444445&amp;_ipg=2&amp;_mPrRngCbx=1&amp;_pgn=1&amp;_sop=1&amp;_udhi=73%2C01&amp;_udlo=36%2C51</itemSearchURL>
</findItemsByKeywordsResponse>
"""


def test_EbayFindItems_1():
    """Test access to Ebay site and download of XML."""
    from clair.network import EbayFindItems
    from ebay.utils import set_config_file
    
    set_config_file("../python-ebay.apikey")
    
    f = EbayFindItems()
    xml = f.call_ebay(keywords="ipod", 
                      entries_per_page=2, 
                      page_number=1, 
                      min_price=50, 
                      max_price=100, 
                      currency="USD", 
                      time_from=datetime.utcnow() + timedelta(minutes=10), 
                      time_to=  datetime.utcnow() + timedelta(days=2))
#    print xml
    
    root = etree.fromstring(xml)
    print etree.tostring(root, pretty_print=True)
    ack = root.find("{http://www.ebay.com/marketplace/search/v1/services}ack").text
    assert ack == "Success"


def test_EbayFindItems_2():
    """Test test parsing of XML response."""
    from clair.network import EbayFindItems
    
    f = EbayFindItems()
    listings = f.parse_xml(EBAY_findItemsByKeywords_RESPONSE)
    
    print listings
    print
    print listings[["title", "price"]]
    
    #There are two listings (items) in the response
    assert len(listings) == 2


if __name__ == '__main__':
    test_EbayFindItems_2()
    
    pass #pylint: disable=W0107