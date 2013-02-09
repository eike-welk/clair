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
            
#import pytest #contains `skip`, `fail`, `raises`, `config`
from numpy import isnan
from datetime import datetime


def test_ListingsXMLConverter():
    """Test conversion of listings to and from XML"""
    from clair.coredata import make_listing_frame, ListingsXMLConverter
    
    ls = make_listing_frame(2)
    ls["id"] = ["eb-123", "eb-456"]
    ls["training_sample"][0] = True 
    ls["query_string"][0] = "Nikon D90"
    
    #TODO: special handling for lists
#    ls["expected_products"][0] = ["nikon-d90", "qwert"]
#    ls["products"][0] = []
    
    ls["thumbnail"][0] = "www.some.site/dir/to/thumb.pg"
    ls["image"][0] = "www.some.site/dir/to/img.pg"
    
    ls["title"] = [u"qwert", u"müähö"]
    ls["description"][0] = "asdflkhglakjh lkasdfjlakjf"
    ls["active"][0] = False
    ls["sold"][0] = False
    ls["currency"][0] = "EUR"
    ls["price"][0]    = 400.
    ls["shipping"][0] = 12.
    ls["type"][0] = "auction"
#    ls["time"][0] = dprs.parse(li.time.pyval) 
    ls["time"][0] = datetime(2013,1,15)
    ls["location"][0] = u"Köln"
    ls["country"][0] = "DE"
    ls["condition"][0] = 0.7
    ls["server"][0] = "Ebay-Germany"
    ls["server_id"][0] = "123" #ID of listing on server
#    ls["data_directory"] = ""
    ls["url_webui"][0] = "www.some.site/dir/to/web-page.html"
#     ls["server_repr"][0] = nan
    #Put our IDs into index
    ls.set_index("id", drop=False, inplace=True, 
                 verify_integrity=True)
    
    
    print ls
    print
    
    conv = ListingsXMLConverter()
    
    xml = conv.to_xml(ls)
    print xml
    
    ls2 = conv.from_xml(xml)
    print ls2
    
    for col in ls.columns:
        print "col:", col
        for i in range(len(ls.index)):
            if ls[col][i] != ls2[col][i]:
                print "i:", i, "ls[col][i] =", ls[col][i], "ls2[col][i] =", ls2[col][i]
                print "    ",  "ls[col][i] =", type(ls[col][i]), "ls2[col][i] =", type(ls2[col][i])
                if isnan(ls[col][i]) and isnan(ls2[col][i]):
                    continue
            assert ls[col][i] == ls2[col][i]



if __name__ == "__main__":
    test_ListingsXMLConverter()