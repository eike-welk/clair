# -*- coding: utf-8 -*-
###############################################################################
#    Clair - Project to discover prices on e-commerce sites.                  #
#                                                                             #
#    Copyright (C) 2016 by Eike Welk                                          #
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
Test module ``xmlio``, which performs
input and Output of data in XML format.
"""

from __future__ import division
from __future__ import absolute_import

import pytest #contains `skip`, `fail`, `raises`, `config` #IGNORE:W0611

import os
import glob
import time
import os.path as path
from datetime import datetime

from numpy import isnan #, nan #IGNORE:E0611
#from pandas.util.testing import assert_frame_equal

import logging
from logging import info
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime



def relative(*path_comps):
    "Create file path_comps that are relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_comps))


def make_test_listings():
    """
    Create a DataFrame with some data.
    
    Contains 3 listings: 
    row 0: contains realistic data; rows 1, 2 contain mainly None, nan.
    """
    from clair.dataframes import make_listing_frame
    
    fr = make_listing_frame(3)
    #All listings need unique ids
    fr["id"] = ["eb-123", "eb-456", "eb-457"]
    
    fr.ix[0, "training_sample"] = True 
    fr.ix[0, "search_tasks"] = ["s-nikon-d90"]
#    fr.ix[0, "query_string"] = "Nikon D90"

    fr.set_value(0, "expected_products", ["nikon-d90", "nikon-sb-24"])
    fr.ix[0, "products"] = ["nikon-d90"]
    fr.ix[0, "products_absent"] = ["nikon-sb-24"]
    
    fr.ix[0, "thumbnail"] = "www.some.site/dir/to/thumb.pg"
    fr.ix[0, "image"] = "www.some.site/dir/to/img.pg"
    fr["title"] = [u"Nikon D90 super duper!", u"<>müäh", None]
    fr.ix[0, "description"] = "Buy my old Nikon D90 camera <b>now</b>!"
    fr.set_value(0, "prod_spec", {"Marke":"Nikon", "Modell":"D90"})
    fr.ix[0, "active"] = False
    fr.ix[0, "sold"] = False
    fr.ix[0, "currency"] = "EUR"
    fr.ix[0, "price"]    = 400.
    fr.ix[0, "shipping"] = 12.
    fr.ix[0, "type"] = "auction"
    fr["time"] = [datetime(2013,1,10), datetime(2013,2,2), datetime(2013,2,3)]
    fr.ix[0, "location"] = u"Köln"
    fr.ix[0, "postcode"] = u"50667"
    fr.ix[0, "country"] = "DE"
    fr.ix[0, "condition"] = 0.7
    fr.ix[0, "server"] = "Ebay-Germany"
    fr.ix[0, "server_id"] = "123" #ID of listing on server
    fr.ix[0, "final_price"] = True
#    fr["data_directory"] = ""
    fr.ix[0, "url_webui"] = "www.some.site/dir/to/web-page.html"
#     fr.ix[0, "server_repr"] = nan
    #Put our IDs into index
    fr.set_index("id", drop=False, inplace=True, 
                 verify_integrity=True)
#    print fr
    return fr

    
def assert_frames_equal(fr1, fr2):
    """
    Asserts that two data frame objects are equal. 
    Handles ``nan`` and ``None`` right.
    """
    assert all(fr1.columns == fr2.columns)
    
    #Compare the two DataFrame objects. Complications:
    #* (nan == nan) == False
    #* (None == None) == False; Special treatment of None inside DataFrame.
    for col in fr1.columns:
        for i in range(len(fr1.index)):
            try:
                assert fr1[col][i] == fr2[col][i]
            except AssertionError:
                if isinstance(fr1[col][i], float) and \
                   isinstance(fr2[col][i], float) and \
                   isnan(fr1[col][i]) and isnan(fr2[col][i]):
                    continue
                
                print "col =", repr(col), "; i =", i
                print "fr1[col][i] =", fr1[col][i], \
                      "; type(fr1[col][i]) =", type(fr1[col][i])  
                print "fr2[col][i] =", fr2[col][i], \
                       "; type(fr2[col][i]) =", type(fr2[col][i])
                    
                raise

    
    
@pytest.skip("XMLConverterListings is broken")          #IGNORE:E1101
def test_ListingsXMLConverter():
    """Test conversion of listings to and from XML"""
    from clair.xmlio import XMLConverterListings
    
    #Create DataFrame with 3 listings. 
    #row 0: contains realistic data; rows 1, 2 contain mainly None, nan.
    ls1 = make_test_listings()
    print ls1
    print
    
    conv = XMLConverterListings()
    
    #The test: convert to XML and back.
    xml = conv.to_xml(ls1)
    print xml
    ls2 = conv.from_xml(xml)
    print ls2
    print 
    assert_frames_equal(ls1, ls2)


@pytest.skip("XmlIOBigFrame is broken")          #IGNORE:E1101
def test_XmlBigFrameIO_read_write_text():
    """Test reading and writing text files"""
    from clair.xmlio import XmlIOBigFrame
    
    testdata_dir = relative("../../test-data")
    basename = "test-file"
    
    #Remove test files
    testdata_pattern = path.join(testdata_dir, basename) + "*"
    os.system("rm " + testdata_pattern)
    
    #Create test object
    xml_io = XmlIOBigFrame(testdata_dir, basename, None)

    #Create nonsense files
    fname_ok = xml_io.make_filename(datetime(2012, 3, 3), 0, False)
    fname_bad = fname_ok[:len(basename)+1] + "xx" + fname_ok[len(basename)+3:]
    path_empty = path.join(testdata_dir, fname_ok)
    path_bad1 = path.join(testdata_dir, fname_ok + ".old")
    path_bad2 = path.join(testdata_dir, fname_bad)
    os.system("touch " + path_empty)
    os.system("touch " + path_bad1)
    os.system("touch " + path_bad2)
    
    #Write some files
    xml_io.write_text("Contents of test file from January, 1.", 
                      datetime(2012, 1, 1), False, False)
    xml_io.write_text("Contents of test file from January, 2.", 
                      datetime(2012, 1, 1), False, False)
    xml_io.write_text("Contents of test file from January, 3.", 
                      datetime(2012, 1, 1), False, False)
    xml_io.write_text("Contents of test file from February, 1.", 
                      datetime(2012, 2, 10, 11, 11), False, False)
    xml_io.write_text("Contents of test file from February, 2.", 
                      datetime(2012, 2, 20, 12, 12), False, False)
    
    #Show which files exist
    os.system("ls " + testdata_dir)
    
    #Read the files that were just written, test if we get right contents.
    texts = xml_io.read_text(datetime(2012, 1, 1), datetime(2012, 1, 1))
    print texts
    assert len(texts) == 3
    assert texts == ["Contents of test file from January, 1.",
                     "Contents of test file from January, 2.",
                     "Contents of test file from January, 3."]
    texts = xml_io.read_text(datetime(2012, 1, 1), datetime(2012, 2, 1))
    print texts
    assert len(texts) == 5

    
@pytest.skip("XmlIOBigFrame, XMLConverterListings are broken.")          #IGNORE:E1101    
def test_XmlBigFrameIO_read_write_dataframe():
    """Test reading and writing DataFrame objects as XML"""
    from clair.xmlio import XmlIOBigFrame, XMLConverterListings
    
    testdata_dir = relative("../../test-data")
    basename = "test-listings"
    
    #Remove test files
    testdata_pattern = path.join(testdata_dir, basename) + "*"
    os.system("rm " + testdata_pattern)
    
    #Create test data
    frame1 = make_test_listings()
#    print frame1
    
    #Create test object
    xml_io = XmlIOBigFrame(testdata_dir, basename, XMLConverterListings())
    #datetime(2013,1,10), datetime(2013,2,2), datetime(2013,2,3)
    
    #Write and read XML files, written data must be same as read data.
    xml_io.write_data(frame1)
#    xml_io.write_data(frame1, datetime(2013,1,1), datetime(2013,1,1))
    frame2 = xml_io.read_data()
#    print frame2
    assert_frames_equal(frame1, frame2)
    #Count the created files
#    os.system("ls " + testdata_dir)
    files_glob = glob.glob(testdata_pattern)
    assert len(files_glob) == 2
    print
    
    #Write files again, the algorithm must create new files.
    #read them, it must not confuse the algorithm
    xml_io.write_data(frame1)
    frame2 = xml_io.read_data()
    assert_frames_equal(frame1, frame2)
    #Count the created files
#    os.system("ls " + testdata_dir)
    files_glob = glob.glob(testdata_pattern)
    assert len(files_glob) == 4
    print
    
    #Write files in overwrite mode, read them, compare
    xml_io.write_data(frame1, overwrite=True)
    frame2 = xml_io.read_data()
    assert_frames_equal(frame1, frame2)
    #Count the created files
#    os.system("ls " + testdata_dir)
    files_glob = glob.glob(testdata_pattern)
    assert len(files_glob) == 2


@pytest.skip("XMLConverterProducts is broken")          #IGNORE:E1101
def test_ProductXMLConverter():
    """Test conversion of product objects from and to XML"""
    from clair.xmlio import Product, XMLConverterProducts
    
    pl1 = [Product("a1", "A1 thing", "The A1 is great.", ["Foo", "A2"], 
                        ["bar", "baz"]),
           Product("a2", "PRoduct B1",),
           Product("", "", "", [], [])
           ]
    
    conv = XMLConverterProducts()
    
    #Convert dict of products to XML
    pd_xml = conv.to_xml(pl1)
    print pd_xml
    #Convert XML back to dict of products
    pl2 = conv.from_xml(pd_xml)
    print pl2
    #Conversion to XML and back must result in equal data structure
    assert pl1 == pl2
    print 
    
    #None values in ``important_words``, ``description`` should not cause crash
    pbad2 = Product("bad2")
    pbad2.categories = None
    pbad2.important_words = None
    pd3 = [pbad2]
    
    pd_xml = conv.to_xml(pd3)
    print pd_xml
    pd4 = conv.from_xml(pd_xml)
    print pd4
    assert pd4[0].id == "bad2"
    
    
@pytest.skip("XMLConverterTasks is broken.")          #IGNORE:E1101
def test_TaskXMLConverter():
    """Test conversion of product objects from and to XML"""
    from clair.xmlio import SearchTask, UpdateTask, XMLConverterTasks
    
    td1 = [SearchTask("s-nikon-d90", datetime(2000, 1, 1, 20, 30), 
                      "ebay-de", "Nikon D90", "daily", 500, 170, 700, "EUR", 
                      ["nikon-d90", "nikon-sb24"]),
           SearchTask("s-nikon-d70", datetime(2000, 1, 1, 10, 10), 
                      "ebay-de", "Nikon D70",),
           SearchTask("s-nikon-sb24", datetime(2000, 1, 1, 2, 3), 
                      "ebay-de", "Nikon SB24",),
           ]
    
    conv = XMLConverterTasks()
    
    #Convert dict of products to XML
    td_xml = conv.to_xml(td1)
    print td_xml
    #Convert XML back to dict of products
    td2 = conv.from_xml(td_xml)
    print td2
    
    #Conversion to XML and back must result in equal data structure
    assert td1 == td2
    
    #Update tasks must not confuse the converter
    td1.append(UpdateTask("update-1", datetime(2000, 1, 1, 20, 20), "ebay-de"))
    td_xml = conv.to_xml(td1)
    
    
@pytest.skip("XmlIOSmallObject is broken")          #IGNORE:E1101
def test_XmlSmallObjectIO():
    """Test file writer object for small data structures."""
    from clair.xmlio import Product, XMLConverterProducts, XmlIOSmallObject
    
    testdata_dir = relative("../../test-data")
    basename = "test-products"
    
    #Remove test files
    testdata_pattern = path.join(testdata_dir, basename) + "*"
    os.system("rm " + testdata_pattern)
#    os.system("ls " + testdata_dir)
    
    pd1 = [Product("a1", "A1 thing", "The A1 is great."),
           Product("a2", "Foo A2", "", ["Foo", "A2"]),
           Product("b1", "PRoduct B1", "The B2 is versatile."),
           ]
    
    io = XmlIOSmallObject(testdata_dir, basename, XMLConverterProducts())
    
    #Write into empty directory
    io.write_data(pd1)
    pd2 = io.read_data()
#    os.system("ls " + testdata_dir)
    assert pd1 == pd2
    
    #Write into directory with old file
    pd1[0].name = "Foo Bar"
    io.write_data(pd1)
    pd2 = io.read_data()
#    os.system("ls " + testdata_dir)
    assert pd1 == pd2

    
@pytest.skip("DataStore is broken")          #IGNORE:E1101
def test_DataStore():
    """
    Test the data storage object.
    """
    from clair.xmlio import DataStore
    
    d = DataStore()
    
    info("Robust behavior when no data is present. - Must not crash")
    d.read_data(relative("."))
    
    info("")
    info("Must load real data")
    d.read_data(relative("../../example-data"))
    assert len(d.products) > 0
    assert len(d.tasks) > 0
    assert len(d.listings) > 0
    
    print "finished"
    

@pytest.skip("DataStore is broken")          #IGNORE:E1101
def test_DataStore_update_expected_products():
    """
    Test updating the "expected_product" fields of listings and tasks. 
    """
    from clair.xmlio import DataStore
    
    print "start"
    
    #Read example data from disk
    data = DataStore()
    data.read_data(relative("../../example-data"))
    
    #remember existing data frame for later tests
    old_listings = data.listings.copy()

    #Find a test task and test listing
    test_listing = data.listings.ix[0]
    test_task_id = test_listing["search_tasks"][0]
    test_task = None
    for test_task in data.tasks:
        if test_task.id == test_task_id:
            break
    #Put additional expected product into test listing
    data.listings["expected_products"][0] += ["foo"]
    
#    print test_listing[["title", "search_tasks", "expected_products"]]
#    print test_task_id
#    print test_task
#    print

    #The test:
    #The new expected product "foo" must be put into ``test task``, and into all
    #listings that are associated with ``test task``.
    data.update_expected_products(test_task_id)
    
    #The expected products field in the task must contain the new product "foo"
    print test_task
    assert "foo" in test_task.expected_products
    
    #All listings that are associated with test task must contain new listing foo
    new_exp_prods = test_task.expected_products
    n_prods = 0
    for _, listing in data.listings.iterrows():
        if test_task_id in listing["search_tasks"]:
#            print listing["id"], listing["expected_products"], listing["title"]
            assert "foo" in listing["expected_products"]
            assert listing["expected_products"] == new_exp_prods
            n_prods += 1
    assert n_prods > 10
    
    #Compare old listings with current listings:
    #All data must be the same, except column "expected_products"
    del data.listings["expected_products"]
    del old_listings["expected_products"]
    #Indexes must be sorted for the comparison
    data.listings = data.listings.sort_index()
    old_listings = old_listings.sort_index()
    #The equality test itself
    assert_frames_equal(old_listings, data.listings)
    
    print "finished"
    

@pytest.skip("DataStore is broken")          #IGNORE:E1101
def test_DataStore_write_expected_products_to_listings():
    """
    Test writing the "expected_product" fields of listings. 
    """
    print "Start"
    from clair.xmlio import DataStore
    
    #Read example data from disk
    data = DataStore()
    data.read_data(relative("../../example-data"))
    #remember existing data frame for later tests
    old_listings = data.listings.copy()

    #Find a test task
    test_task = data.tasks[1]
    test_task_id = test_task.id
    
    #Put new contents into task's "expected_products" field
    test_task.expected_products = ["foo", "bar", "baz"]
    
    print test_task_id
    print test_task
    print

    #The test:
    #The new expected product "foo" must be put into ``test task``, and into all
    #listings that are associated with ``test task``.
    data.write_expected_products_to_listings(test_task_id)
    
    #All listings that are associated with ``test_task`` must contain new 
    #listings ``["foo", "bar", "baz"]``
    n_prods = 0
    for _, listing in data.listings.iterrows():
        if test_task_id in listing["search_tasks"]:
#            print listing["id"], listing["expected_products"], listing["title"]
            assert listing["expected_products"] == test_task.expected_products
            n_prods += 1
    assert n_prods > 10
    
    #Compare old listings with current listings:
    #All data must be the same, except column "expected_products"
    del data.listings["expected_products"]
    del old_listings["expected_products"]
    #Indexes must be sorted for the comparison
    data.listings = data.listings.sort_index()
    old_listings = old_listings.sort_index()
    #The equality test itself
    assert_frames_equal(old_listings, data.listings)
    
    print "Finished"
    

    
if __name__ == "__main__":
#    test_make_price_frame()
#    test_make_price_id()
#    test_ListingsXMLConverter()
#    test_TaskXMLConverter()
#    test_XmlBigFrameIO_read_write_text()
#    test_XmlBigFrameIO_read_write_dataframe()
#    test_Record()
#    test_ProductXMLConverter()
#    test_XmlSmallObjectIO()
#    test_DataStore()
#    test_DataStore_update_expected_products()
#    test_DataStore_write_expected_products_to_listings()
    
    pass
