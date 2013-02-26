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
Test text processing module.
"""

from __future__ import division
from __future__ import absolute_import              
            
import pytest #contains `skip`, `fail`, `raises`, `config`

import os
import os.path as path
import glob
import time
from datetime import datetime

from numpy import isnan, nan
import pandas as pd

import logging
from logging import info
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime



def relative(*path_components):
    "Create file a path that is relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_components))


def make_test_listings():
    """
    Create a DataFrame with some data.
    """
    from clair.coredata import make_listing_frame
    
    fr = make_listing_frame(3)
    #All listings need unique ids
    fr["id"] = ["eb-123", "eb-456", "eb-457"]
    
    fr["training_sample"][0] = True 

    fr["expected_products"][0] = ["nikon-d90", "nikon-sb-24"]
    fr["products"][0] = ["nikon-d90"]
    fr["products_absent"][0] = ["nikon-sb-24"]
    
    fr["title"] = [u"Nikon D90 super duper!", u"<>müäh", None]
    fr["description"][0] = "Buy my old Nikon D90 camera <b>now</b>!"
    fr["prod_spec"][0] = {"Marke":"Nikon", "Modell":"D90"}

    #Put our IDs into index
    fr.set_index("id", drop=False, inplace=True, 
                 verify_integrity=True)
    return fr


def test_HtmlTool():
    """Test the HTML to pure text conversion."""
    from clair.textprocessing import HtmlTool
    
    text = HtmlTool.remove_html("<b>Bold</b> text.   <p>Paragraph.</p> 3 &gt; 2")
    print text
    assert text == "Bold text. Paragraph. 3 > 2"
    
    assert HtmlTool.remove_html(None) == ""
    assert HtmlTool.remove_html(nan) == ""
    

def test_DataStore():
    """Test the data storage object."""
    from clair.textprocessing import DataStore
    
    d = DataStore()
    
    info("Robust behavior when no data is present. - Must not crash")
    d.read_data(relative("."))
    
    info("")
    info("Must load real data")
    d.read_data(relative("../../example-data"))
    assert len(d.products) > 0
    assert len(d.tasks) > 0
    assert len(d.listings) > 0
    
    
def test_CollectText():
    """Test text collection object"""
    from clair.textprocessing import CollectText
    
    #Convert some test data
    c = CollectText()
    l1 = make_test_listings()
    c.insert_listings(l1)
#    print c.texts
    print c.texts.to_string()
    assert len(c.texts) == 3
    assert set(c.texts.columns) == set(["title", "description", "prod_spec"])
    
    #Process the example listings
    c = CollectText()
    c.insert_listings_from_files(relative("../../example-data"))
    print c.texts
#    print c.texts.to_string()
    assert len(c.texts) >= 100
    assert set(c.texts.columns) == set(["title", "description", "prod_spec"])
    
    lt = c.get_listings_text()
#    print lt
    assert len(lt) == len(c.texts)
    assert isinstance(lt.ix[3], unicode)
#    assert  lt.map(lambda u: isinstance(u, unicode)).all()

    tt = c.get_total_text()
#    print tt
    print "len(tt) =", len(tt)
    assert isinstance(tt, unicode) 
    assert len(tt) > 1000
    
    print "finished"



if __name__ == "__main__":
#    test_HtmlTool()
#    test_DataStore()
    test_CollectText()
    
    pass #IGNORE:W0107
