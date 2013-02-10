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
Put module description here.
"""

from __future__ import division
from __future__ import absolute_import              


from datetime import datetime
import dateutil.parser as dprs 
from numpy import nan
import pandas as pd
from lxml import etree, objectify



def make_listing_frame(nrows):
    """
    Create empty DataFrame with `nrows` listings/auctions.
    
    Each row represents a listing. The columns represent the listing's 
    attributes. The object contains no data, nearly all values are None or nan.
    
    TODO: Put into central location. 
    """
    index=[str(i) for i in range(nrows)]
    
    listings = pd.DataFrame(index=index)
    listings["id"]                = None  #internal unique ID of each listing.
    listings["training_sample"]   = False #This is training sample if True
    listings["query_string"]      = None  #String with search keywords
    listings["expected_products"] = None  #list of product IDs
    
    listings["products"]    = None  #Products in this listing. List of DetectedProduct

    listings["thumbnail"]   = None          
    listings["image"]       = None          
    
    listings["title"]       = None
    listings["description"] = None
    #TODO: include ``ItemSpecifics``: name value pairs eg.: {"megapixel": "12"}
    #TODO: include bid_count?
    listings["active"]      = nan   #you can still buy it if True
    listings["sold"]        = nan   #successful sale if True
    listings["currency"]    = None  #currency for price EUR, USD, ...
    listings["price"]       = nan   #price of all items in listing
    listings["shipping"]    = nan   #shipping cost
    listings["type"]        = None  #auction, fixed-price, unknown
    listings["time"]        = None  #Time when price is/was valid. End time in case of auctions
    listings["location"]    = None  #Location of item (pre sale)
    listings["country"]     = None  #Country of item location
    listings["condition"]   = nan   #1.: new, 0.: completely unusable
    
    listings["server"]      = None  #string to identify the server
    listings["server_id"]   = None  #ID of listing on the server
#    listings["data_dir"]    = None  #Images, html, ... might be stored here
    listings["url_webui"]   = None  #Link to web representation of listing.
#    listings["server_repr"] = None  #representation of listing on server (XML)

    return  listings
    


class ListingsXMLConverter:
    """
    Convert listings to and from XML
    
    Unicode introduction
    http://docs.python.org/2/howto/unicode.html
    
    TODO: XML escapes for description
    http://wiki.python.org/moin/EscapingXml
    """
    E = objectify.E

    def to_xml_list(self, tag, el_list):
        """Convert lists, wrap each element of a list with a tag."""
        if el_list is None:
            return [None]
        E = ListingsXMLConverter.E
        node = getattr(E, tag)
        xml_nodes = [node(el) for el in el_list]
        return xml_nodes
    

    def to_xml(self, listings):
        """Convert DataFrame with listings/auctions to XML."""
        E = ListingsXMLConverter.E

        root_xml = E.listings(
            E.version("0.1") )
        for i in range(len(listings.index)):
            li = listings.ix[i]
            li_xml = E.listing(
                E.id(li["id"]),
                E.training_sample(bool(li["training_sample"])),
                E.query_string(li["query_string"]),
                E.expected_products(*self.to_xml_list(
                                        "product", li["expected_products"])),
                E.products(*self.to_xml_list("product", li["products"])),
                E.thumbnail(li["thumbnail"]),
                E.image(li["image"]),
                E.title(li["title"]),
                E.description(li["description"]),
                E.active(float(li["active"])),
                E.sold(float(li["sold"])),
                E.currency(li["currency"]),
                E.price(float(li["price"])),
                E.shipping(float(li["shipping"])),
                E.type(li["type"]),
                E.time(li["time"]),
                E.location(li["location"]),
                E.country(li["country"]),
                E.condition(float(li["condition"])),
                E.server(li["server"]),
                E.server_id(li["server_id"]),
                E.url_webui(li["url_webui"]) )
            root_xml.append(li_xml)
        
#        doc_xml = etree.ElementTree(root_xml)
        doc_str = etree.tostring(root_xml, pretty_print=True)
        return doc_str 

    
    def from_xml_list(self, tag, xml_list):
        """Convert a repetition of XML elements into a Python list."""
        if isinstance(xml_list, objectify.NoneElement):
            return None
        
        elements = xml_list[tag]
        el_list = []
        for el in elements:
            #TODO: convert structured elements.
            el_list.append(el.pyval)
        return el_list
        
        
    def from_xml(self, xml):
        """Convert XML string into DataFrame with listings/auctions"""
        root_xml = objectify.fromstring(xml)
#        print objectify.dump(root_xml)
        
        version = root_xml.version.text
        assert version == "0.1"
               
        listing_xml = root_xml.listing
        nrows = len(listing_xml)
        listings = make_listing_frame(nrows)
        for i, li in enumerate(listing_xml):    
            listings["id"][i] = li.id.pyval 
            listings["training_sample"][i] = li.training_sample.pyval 
            listings["query_string"][i] = li.query_string.pyval
            listings["expected_products"][i] = self.from_xml_list(
                                            "product", li.expected_products)
            listings["products"][i] = self.from_xml_list(
                                            "product", li.products)
            listings["thumbnail"][i] = li.thumbnail.pyval
            listings["image"][i] = li.image.pyval
            listings["title"][i] = li.title.pyval 
            listings["description"][i] = li.description.pyval
            listings["active"][i] = li.active.pyval
            listings["sold"][i] = li.sold.pyval
            listings["currency"][i] = li.currency.pyval
            listings["price"][i]    = li.price.pyval
            listings["shipping"][i] = li.shipping.pyval
            listings["type"][i] = li.type.pyval
            listings["time"][i] = dprs.parse(li.time.pyval) \
                                  if li.time.pyval is not None else None
            listings["location"][i] = li.location.pyval
            listings["country"][i] = li.country.pyval
            listings["condition"][i] = li.condition.pyval
            listings["server"][i] = li.server.pyval
            listings["server_id"][i] = li.server_id.pyval #ID of listing on server
#            listings["data_directory"] = ""
            listings["url_webui"][i] = li.url_webui.pyval
#            listings["server_repr"][i] = nan

        #Put our IDs into index
        listings.set_index("id", drop=False, inplace=True, 
                           verify_integrity=True)
        return listings
