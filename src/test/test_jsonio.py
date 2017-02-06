# -*- coding: utf-8 -*-
###############################################################################
#    Clair - Project to discover prices on e-commerce sites.                  #
#                                                                             #
#    Copyright (C) 2017 by Eike Welk                                          #
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
Test module ``jsonio``, which performs
input and Output of data in JSON format.
"""

# import pytest #contains `skip`, `fail`, `raises`, `config` #IGNORE:W0611

# import os
# import glob
# import time
from pprint import pprint 
import os.path as path
from datetime import datetime

from numpy import isnan #, nan #IGNORE:E0611
#from pandas.util.testing import assert_frame_equal

# import logging
# from logging import info
# logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
#                     level=logging.DEBUG)
# #Time stamps must be in UTC
# logging.Formatter.converter = time.gmtime



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
    fr["title"] = ["Nikon D90 super duper!", "<>müäh", None]
    fr.ix[0, "description"] = "Buy my old Nikon D90 camera <b>now</b>!"
    fr.set_value(0, "prod_spec", {"Marke":"Nikon", "Modell":"D90"})
    fr.ix[0, "active"] = False
    fr.ix[0, "sold"] = False
    fr.ix[0, "currency"] = "EUR"
    fr.ix[0, "price"]    = 400.
    fr.ix[0, "shipping"] = 12.
    fr.ix[0, "type"] = "auction"
    fr["time"] = [datetime(2013,1,10), datetime(2013,2,2), datetime(2013,2,3)]
    fr.ix[0, "location"] = "Köln"
    fr.ix[0, "postcode"] = "50667"
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
                
                print("col =", repr(col), "; i =", i)
                print("fr1[col][i] =", fr1[col][i], \
                      "; type(fr1[col][i]) =", type(fr1[col][i]))  
                print("fr2[col][i] =", fr2[col][i], \
                       "; type(fr2[col][i]) =", type(fr2[col][i]))
                    
                raise
    

def test_JsonWriter_convert_to_dict():
    print('Start:')
    from clair.descriptors import TableDescriptor, FieldDescriptor as FD, \
                                  FloatD, StrD, DateTimeD
    from clair.dataframes import make_data_frame
    from clair.jsonio import JsonWriter
    
    #Create regular dataframe
    desc = TableDescriptor(
            'test_table_simple', '1.0', 'ttb', 'A simple table for testing.', 
            [FD('text', StrD, None, 'A text field.'),
             FD('num', FloatD, None, 'An numeric field.'),
#             FD('date', DateTimeD, None, 'A date and time field.'),
             ])
    frame = make_data_frame(desc, 3)
    frame.iloc[0] = ['a', 10]
    frame.iloc[1] = ['b', 11]
    frame.iloc[2] = ['c', 12]
    frame = frame.set_index('text', False)
    #add extra column that should not be saved
    frame['extra'] = [31, 32, 33]
    print(frame)
    
    wr = JsonWriter(desc)
    d = wr._convert_to_dict(frame)
    pprint(d)
    
    # Test existence of some of the data
    assert d['2_rows'][0]['text'] == 'a'
    assert d['2_rows'][0]['num'] == 10
    assert d['2_rows'][2]['text'] == 'c'
    assert d['2_rows'][2]['num'] == 12
    
    # Extra column must not be in generated dict
    assert 'extra' not in d['2_rows'][0]
    # Extra column must still be in original dataframe
    assert 'extra' in frame.columns

    
    
#@pytest.skip("XmlIOBigFrame is broken")          #IGNORE:E1101
#def test_XmlBigFrameIO_read_write_text():
#    """Test reading and writing text files"""
#    from clair.xmlio import XmlIOBigFrame
#    
#    testdata_dir = relative("../../test-data")
#    basename = "test-file"
#    
#    #Remove test files
#    testdata_pattern = path.join(testdata_dir, basename) + "*"
#    os.system("rm " + testdata_pattern)
#    
#    #Create test object
#    xml_io = XmlIOBigFrame(testdata_dir, basename, None)
#
#    #Create nonsense files
#    fname_ok = xml_io.make_filename(datetime(2012, 3, 3), 0, False)
#    fname_bad = fname_ok[:len(basename)+1] + "xx" + fname_ok[len(basename)+3:]
#    path_empty = path.join(testdata_dir, fname_ok)
#    path_bad1 = path.join(testdata_dir, fname_ok + ".old")
#    path_bad2 = path.join(testdata_dir, fname_bad)
#    os.system("touch " + path_empty)
#    os.system("touch " + path_bad1)
#    os.system("touch " + path_bad2)
#    
#    #Write some files
#    xml_io.write_text("Contents of test file from January, 1.", 
#                      datetime(2012, 1, 1), False, False)
#    xml_io.write_text("Contents of test file from January, 2.", 
#                      datetime(2012, 1, 1), False, False)
#    xml_io.write_text("Contents of test file from January, 3.", 
#                      datetime(2012, 1, 1), False, False)
#    xml_io.write_text("Contents of test file from February, 1.", 
#                      datetime(2012, 2, 10, 11, 11), False, False)
#    xml_io.write_text("Contents of test file from February, 2.", 
#                      datetime(2012, 2, 20, 12, 12), False, False)
#    
#    #Show which files exist
#    os.system("ls " + testdata_dir)
#    
#    #Read the files that were just written, test if we get right contents.
#    texts = xml_io.read_text(datetime(2012, 1, 1), datetime(2012, 1, 1))
#    print texts
#    assert len(texts) == 3
#    assert texts == ["Contents of test file from January, 1.",
#                     "Contents of test file from January, 2.",
#                     "Contents of test file from January, 3."]
#    texts = xml_io.read_text(datetime(2012, 1, 1), datetime(2012, 2, 1))
#    print texts
#    assert len(texts) == 5
#
#    
#@pytest.skip("XmlIOBigFrame, XMLConverterListings are broken.")          #IGNORE:E1101    
#def test_XmlBigFrameIO_read_write_dataframe():
#    """Test reading and writing DataFrame objects as XML"""
#    from clair.xmlio import XmlIOBigFrame, XMLConverterListings
#    
#    testdata_dir = relative("../../test-data")
#    basename = "test-listings"
#    
#    #Remove test files
#    testdata_pattern = path.join(testdata_dir, basename) + "*"
#    os.system("rm " + testdata_pattern)
#    
#    #Create test data
#    frame1 = make_test_listings()
##    print frame1
#    
#    #Create test object
#    xml_io = XmlIOBigFrame(testdata_dir, basename, XMLConverterListings())
#    #datetime(2013,1,10), datetime(2013,2,2), datetime(2013,2,3)
#    
#    #Write and read XML files, written data must be same as read data.
#    xml_io.write_data(frame1)
##    xml_io.write_data(frame1, datetime(2013,1,1), datetime(2013,1,1))
#    frame2 = xml_io.read_data()
##    print frame2
#    assert_frames_equal(frame1, frame2)
#    #Count the created files
##    os.system("ls " + testdata_dir)
#    files_glob = glob.glob(testdata_pattern)
#    assert len(files_glob) == 2
#    print
#    
#    #Write files again, the algorithm must create new files.
#    #read them, it must not confuse the algorithm
#    xml_io.write_data(frame1)
#    frame2 = xml_io.read_data()
#    assert_frames_equal(frame1, frame2)
#    #Count the created files
##    os.system("ls " + testdata_dir)
#    files_glob = glob.glob(testdata_pattern)
#    assert len(files_glob) == 4
#    print
#    
#    #Write files in overwrite mode, read them, compare
#    xml_io.write_data(frame1, overwrite=True)
#    frame2 = xml_io.read_data()
#    assert_frames_equal(frame1, frame2)
#    #Count the created files
##    os.system("ls " + testdata_dir)
#    files_glob = glob.glob(testdata_pattern)
#    assert len(files_glob) == 2
    

    
if __name__ == "__main__":
    test_JsonWriter_convert_to_dict()
    
    pass
