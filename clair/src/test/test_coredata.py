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
import os
import os.path as path
from numpy import isnan, nan
from datetime import datetime


def relative(*path_comps):
    "Create file path_comps that are relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_comps))


def test_ListingsXMLConverter():
    """Test conversion of listings to and from XML"""
    from clair.coredata import make_listing_frame, ListingsXMLConverter
    
    #Create DataFrame with 2 listings. 
    #ls1[0]: contains realistic data; ls1[1] contains mainly None, nan
    ls1 = make_listing_frame(2)
    #All listings need unique ids
    ls1["id"] = ["eb-123", "eb-456"]
    
    ls1["training_sample"][0] = True 
    ls1["query_string"][0] = "Nikon D90"
    
    #TODO: special handling for lists
    ls1["expected_products"][0] = ["nikon-d90", "qwert"]
#    ls1["products"][0] = []
    
    ls1["thumbnail"][0] = "www.some.site/dir/to/thumb.pg"
    ls1["image"][0] = "www.some.site/dir/to/img.pg"
    ls1["title"] = [u"qwert", u"<>müäh"]
    ls1["description"][0] = "asdflkhglakjh lkasdfjlakjf"
    ls1["active"][0] = False
    ls1["sold"][0] = False
    ls1["currency"][0] = "EUR"
    ls1["price"][0]    = 400.
    ls1["shipping"][0] = 12.
    ls1["type"][0] = "auction"
#    ls1["time"][0] = dprs.parse(li.time.pyval) 
    ls1["time"][0] = datetime(2013,1,15)
    ls1["location"][0] = u"Köln"
    ls1["country"][0] = "DE"
    ls1["condition"][0] = 0.7
    ls1["server"][0] = "Ebay-Germany"
    ls1["server_id"][0] = "123" #ID of listing on server
#    ls1["data_directory"] = ""
    ls1["url_webui"][0] = "www.some.site/dir/to/web-page.html"
#     ls1["server_repr"][0] = nan
    #Put our IDs into index
    ls1.set_index("id", drop=False, inplace=True, 
                 verify_integrity=True)
    
    print ls1
    print
    
    conv = ListingsXMLConverter()
    
    #The test: convert to XML and back.
    xml = conv.to_xml(ls1)
    print xml
    ls2 = conv.from_xml(xml)
    print ls2
    print 
    
    #Compare the two DataFrame objects. Complications:
    #* (nan == nan) == False
    #* (None == None) == False; Special treatment of None inside DataFrame.
    for col in ls1.columns:
        print "col:", col
        for i in range(len(ls1.index)):
            if ls1[col][i] != ls2[col][i]:
                print "i:", i, "ls1[col][i] =", ls1[col][i], "; ls2[col][i] =", ls2[col][i]
                print "    ",  "ls1[col][i] =", type(ls1[col][i]), "; ls2[col][i] =", type(ls2[col][i])
                if isnan(ls1[col][i]) and isnan(ls2[col][i]):
                    continue
            assert ls1[col][i] == ls2[col][i]


def test_TextFileIO_write():
    from clair.coredata import TextFileIO
    
    testdata_dir = relative("../../testdata")
    basename = "test-file"
    
    testdata_base = path.join(testdata_dir, basename)
    os.system("rm " + testdata_base + "*")
    
    t = TextFileIO(basename, testdata_dir)
    t.write_text("Contents of test file.", datetime(2012, 1, 15, 12, 30))
    t.write_text("Contents of test file.", datetime(2012, 1, 15, 12, 30))
    t.write_text("Contents of test file.", datetime(2012, 1, 15, 12, 30))
    os.system("ls " + testdata_dir)
    
    texts = t.read_text(None)
    assert len(texts) == 3
    
    

if __name__ == "__main__":
#    test_ListingsXMLConverter()
    test_TextFileIO_write()
    
    pass
