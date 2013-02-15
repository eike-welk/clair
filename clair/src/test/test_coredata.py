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
import glob
import os.path as path
from numpy import isnan, nan
from datetime import datetime


def relative(*path_comps):
    "Create file path_comps that are relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_comps))


def make_test_listings():
    """
    Create a DataFrame with some data.
    
    Contains 3 listings: 
    row 0: contains realistic data; rows 1, 2 contain mainly None, nan.
    """
    from clair.coredata import make_listing_frame
    
    fr = make_listing_frame(3)
    #All listings need unique ids
    fr["id"] = ["eb-123", "eb-456", "eb-457"]
    
    fr["training_sample"][0] = True 
    fr["query_string"][0] = "Nikon D90"
    
    #TODO: special handling for lists
    fr["expected_products"][0] = ["nikon-d90", "qwert"]
#    fr["products"][0] = []
    
    fr["thumbnail"][0] = "www.some.site/dir/to/thumb.pg"
    fr["image"][0] = "www.some.site/dir/to/img.pg"
    fr["title"] = [u"qwert", u"<>müäh", None]
    fr["description"][0] = "asdflkhglakjh lkasdfjlakjf"
    fr["active"][0] = False
    fr["sold"][0] = False
    fr["currency"][0] = "EUR"
    fr["price"][0]    = 400.
    fr["shipping"][0] = 12.
    fr["type"][0] = "auction"
#    fr["time"][0] = dprs.parse(li.time.pyval) 
    fr["time"] = [datetime(2013,1,10), datetime(2013,2,2), datetime(2013,2,3)]
    fr["location"][0] = u"Köln"
    fr["country"][0] = "DE"
    fr["condition"][0] = 0.7
    fr["server"][0] = "Ebay-Germany"
    fr["server_id"][0] = "123" #ID of listing on server
#    fr["data_directory"] = ""
    fr["url_webui"][0] = "www.some.site/dir/to/web-page.html"
#     fr["server_repr"][0] = nan
    #Put our IDs into index
    fr.set_index("id", drop=False, inplace=True, 
                 verify_integrity=True)
    return fr

    
def assert_frames_equal(fr1, fr2):
    """
    Asserts that two data frame objects are equal. 
    Handles ``nan`` and ``None`` right.
    """
    #Compare the two DataFrame objects. Complications:
    #* (nan == nan) == False
    #* (None == None) == False; Special treatment of None inside DataFrame.
    for col in fr1.columns:
        for i in range(len(fr1.index)):
            try:
                assert fr1[col][i] == fr2[col][i]
            except AssertionError:
                if isnan(fr1[col][i]) and isnan(fr2[col][i]):
                    continue
                
                print "col =", col, "; i =", i
                print "fr1[col][i] =", fr1[col][i], \
                      "; type(fr1[col][i]) =", type(fr1[col][i])  
                print "fr2[col][i] =", fr2[col][i], \
                       "; type(fr2[col][i]) =", type(fr2[col][i])
                    
                raise


def test_ListingsXMLConverter():
    """Test conversion of listings to and from XML"""
    from clair.coredata import ListingsXMLConverter
    
    #Create DataFrame with 3 listings. 
    #row 0: contains realistic data; rows 1, 2 contain mainly None, nan.
    ls1 = make_test_listings()
    print ls1
    print
    
    conv = ListingsXMLConverter()
    
    #The test: convert to XML and back.
    xml = conv.to_xml(ls1)
    print xml
    ls2 = conv.from_xml(xml)
    print ls2
    print 
    assert_frames_equal(ls1, ls2)
    

def test_XmlFileIO_read_write_text():
    """Test reading and writing text files"""
    from clair.coredata import XmlBigFrameIO
    
    testdata_dir = relative("../../testdata")
    basename = "test-file"
    
    #Remove test files
    testdata_pattern = path.join(testdata_dir, basename) + "*"
    os.system("rm " + testdata_pattern)
    
    #Create test object
    xml_io = XmlBigFrameIO(basename, testdata_dir, None)

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
    
    
def test_XmlFileIO_read_write_dataframe():
    """Test reading and writing DataFrame objects as XML"""
    from clair.coredata import XmlBigFrameIO, ListingsXMLConverter
    
    testdata_dir = relative("../../testdata")
    basename = "test-file"
    
    #Remove test files
    testdata_pattern = path.join(testdata_dir, basename) + "*"
    os.system("rm " + testdata_pattern)
    
    #Create test data
    frame1 = make_test_listings()
    
    #Create test object
    xml_io = XmlBigFrameIO(basename, testdata_dir, ListingsXMLConverter())
    #datetime(2013,1,10), datetime(2013,2,2), datetime(2013,2,3)
    
    #Write and read XML files, written data must be same as read data.
    xml_io.write_dataframe(frame1)
#    xml_io.write_dataframe(frame1, datetime(2013,1,1), datetime(2013,1,1))
    frame2 = xml_io.read_dataframe()
#    print frame2
    assert_frames_equal(frame1, frame2)
    #Count the created files
#    os.system("ls " + testdata_dir)
    files_glob = glob.glob(testdata_pattern)
    assert len(files_glob) == 2
    print
    
    #Write files again, the algorithm must create new files.
    #read them, it must not confuse the algorithm
    xml_io.write_dataframe(frame1)
    frame2 = xml_io.read_dataframe()
    assert_frames_equal(frame1, frame2)
    #Count the created files
#    os.system("ls " + testdata_dir)
    files_glob = glob.glob(testdata_pattern)
    assert len(files_glob) == 4
    print
    
    #Write files in overwrite mode, read them, compare
    xml_io.write_dataframe(frame1, overwrite=True)
    frame2 = xml_io.read_dataframe()
    assert_frames_equal(frame1, frame2)
    #Count the created files
#    os.system("ls " + testdata_dir)
    files_glob = glob.glob(testdata_pattern)
    assert len(files_glob) == 2


def test_Record():
    """Test Record class"""
    from clair.coredata import Record
    
    r = Record(foo=2, bar="BAR", id=123)
    print r
    
    d = {"A":Record(foo=2, bar="BAR", id=123), 
         "B":Record(foo=3, bar="Boo", id=124)}
    print d
    


if __name__ == "__main__":
#    test_ListingsXMLConverter()
#    test_XmlFileIO_read_write_text()
#    test_XmlFileIO_read_write_dataframe()
    test_Record()
    
    pass
