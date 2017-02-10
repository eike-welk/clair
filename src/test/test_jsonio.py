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

from numpy import isnan #, nan #IGNORE:E0611
import pandas as pd
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
    

def test_JsonWriter__convert_frame_to_dict():
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
             FD('date', DateTimeD, None, 'A date and time field.'),
             ])
    frame = make_data_frame(desc, 3)
    frame.iloc[0] = ['a', 10, pd.Timestamp('2000-01-01')]
    frame.iloc[1] = ['b', 11, pd.Timestamp('2001-02-02')]
    frame.iloc[2] = ['c', 12, pd.Timestamp('2002-03-03')]
#     frame = frame.set_index('text', False)
    #add extra column that should not be saved
    frame['extra'] = [31, 32, 33]
    print(frame)
    
    wr = JsonWriter(desc)
    d = wr._convert_frame_to_dict(frame)
    pprint(d)
    
    # Test existence of some of the data
    assert d['2_rows'][0]['text'] == 'a'
    assert d['2_rows'][0]['num']  == 10
    assert d['2_rows'][2]['text'] == 'c'
    assert d['2_rows'][2]['num']  == 12
    assert d['2_rows'][2]['date']  == '2002-03-03 00:00:00'
    
    # Extra column must not be in generated dict
    assert 'extra' not in d['2_rows'][0]
    # Extra column must still be in original dataframe
    assert 'extra' in frame.columns

    
def test_JsonWriter__convert_dict_to_frame():
    print('Start:')
    from clair.descriptors import TableDescriptor, FieldDescriptor as FD, \
                                  FloatD, StrD, DateTimeD
    from clair.jsonio import JsonWriter
    
    #Create regular dataframe
    desc = TableDescriptor(
            'test_table_simple', '1.0', 'ttb', 'A simple table for testing.', 
            [FD('text', StrD, None, 'A text field.'),
             FD('num',  FloatD, None, 'A numeric field.'),
             FD('num1', FloatD, None, 'An other numeric field.'),
             FD('date', DateTimeD, None, 'A date and time field.'),
             ])
    #Create data dict - column 'num1' is missing
    ddict = \
        {'1_header': {'comment': 'A simple table for testing.',
                      'name': 'test_table_simple',
                      'version': '1.0'},
         '2_rows': [{'num': 10.0, 'text': 'a'},
                    {'num': 11.0, 'text': 'b', 'extra': 'be'},
                    {'num': 12.0, 'text': 'c', 'date': '2002-02-02 00:00:00'},
                    ]}
    
    wr = JsonWriter(desc)
    fr = wr._convert_dict_to_frame(ddict)
    print(fr)
    
    assert isinstance(fr, pd.DataFrame)
    assert fr.shape == (3, 4)
    assert (fr.columns == ['text', 'num', 'num1', 'date']).all()
    # Test existence of some of the data
    assert fr['text'][0] == 'a'
    assert fr['num'][0]  == 10
    assert fr['text'][2] == 'c'
    assert fr['num'][2]  == 12
    assert fr['date'][2]  == pd.Timestamp('2002-02-02')


    
if __name__ == "__main__":
#     test_JsonWriter__convert_frame_to_dict()
#     test_JsonWriter__convert_dict_to_frame()
    
    pass
