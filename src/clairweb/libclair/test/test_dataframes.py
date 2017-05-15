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
Test module ``dataframes``, which contains definitions of the the 
``pandas.DataFrame`` objects that store the application's important data in 2D
tables.
"""
            
import os

import pytest #contains `skip`, `fail`, `raises`, `config` #IGNORE:W0611
import numpy as np
import pandas as pd
import pandas.api.types as pd_types

# import time
# import logging
# logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
#                     level=logging.DEBUG)
# #Time stamps must be in UTC
# logging.Formatter.converter = time.gmtime


    
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
                   np.isnan(fr1[col][i]) and np.isnan(fr2[col][i]):
                    continue
                
                print("col =", repr(col), "; i =", i)
                print("fr1[col][i] =", fr1[col][i], \
                      "; type(fr1[col][i]) =", type(fr1[col][i]))  
                print("fr2[col][i] =", fr2[col][i], \
                       "; type(fr2[col][i]) =", type(fr2[col][i]))
                    
                raise


def test_make_data_series_1():
    """
    Create a data series using a ``libclair.descriptors.FieldDescriptor`` 
    to describe the data type.
    """
    print("Start")
    from libclair.descriptors import (StrD, IntD, FloatD, BoolD, DateTimeD, 
                                   ListD, FieldDescriptor)
    from libclair.dataframes import make_data_series

    fd = FieldDescriptor("foo", FloatD, None, "foo data")
    s = make_data_series(fd, 3)
    s[1] = 1.4
    print(s)
    assert len(s) == 3 
    assert np.isnan(s[0])
    assert s[1] == 1.4
    
    fd = FieldDescriptor("foo", FloatD, 0., "foo data")
    s = make_data_series(fd, 3)
    s[1] = 4.2
    print(s)
    assert len(s) == 3
    assert s[0] == 0
    assert s[1] == 4.2

    fd = FieldDescriptor("foo", IntD, None, "foo data")
    s = make_data_series(fd, 4)
    s[1] = 23
    print(s)
    assert len(s) == 4
    assert np.isnan(s[0])
    assert s[1] == 23
    
    fd = FieldDescriptor("foo", BoolD, None, "foo data")
    s = make_data_series(fd, 3)
    s[1] = True
    print(s)
    assert len(s) == 3
    assert np.isnan(s[0])
    assert s[1] == True

    fd = FieldDescriptor("foo", DateTimeD, None, "foo data")
    s = make_data_series(fd, 3)
    s[1] = pd.Timestamp('2001-01-23 12:30:00')
    print(s)
    assert len(s) == 3
#     assert isnan(s[0])
    assert s[1] == pd.Timestamp('2001-01-23 12:30:00')

    fd = FieldDescriptor("foo", ListD(StrD), None, "foo data")
    s = make_data_series(fd, 3)
    s[1] = ["foo", "bar"]
    print(s)
    assert len(s) == 3
    assert np.isnan(s[0])
    assert s[1] == ["foo", "bar"]


def test_make_data_series_2():
    """
    Create a data series using a ``django.db.models.Field`` 
    to describe the data type.
    """
    print("Start")
    from django.db import models
    from libclair.dataframes import make_data_series

    fd = models.FloatField("foo data")
    s = make_data_series(fd, 3)
    s[1] = 1.4
    print(s)
    assert len(s) == 3 
    assert np.isnan(s[0])
    assert s[1] == 1.4
    
    fd = models.FloatField("foo data", default=0.)
    s = make_data_series(fd, 3)
    s[1] = 4.2
    print(s)
    assert len(s) == 3
    assert s[0] == 0
    assert s[1] == 4.2

    fd = models.IntegerField("foo data")
    s = make_data_series(fd, 4)
    s[1] = 23
    print(s)
    assert len(s) == 4
    assert np.isnan(s[0])
    assert s[1] == 23
    
    fd = models.NullBooleanField("foo data")
    s = make_data_series(fd, 3)
    s[1] = True
    print(s)
    assert len(s) == 3
    assert np.isnan(s[0])
    assert s[1] == True

    fd = models.DateTimeField("foo data")
    s = make_data_series(fd, 3)
    s[1] = pd.Timestamp('2001-01-23 12:30:00')
    print(s)
    assert len(s) == 3
#     assert isnan(s[0])
    assert s[1] == pd.Timestamp('2001-01-23 12:30:00')


def test_make_data_frame_1():
    print("Start")
    from libclair.descriptors import StrD, FloatD, FieldDescriptor, TableDescriptor
    from libclair.dataframes import make_data_frame

    FD = FieldDescriptor
    td = TableDescriptor("foo-table", "1.0", "foot", 
                         "A table for testing purposes.", 
                         [FD("foo", FloatD, None, "foo data"),
                          FD("bar", StrD, None, "bar data")])
    df = make_data_frame(td, 3)
    df.at[1, "foo"] = 23
    df.at[2, "bar"] = "a"
    print(df)
    print("dtypes:\n", df.dtypes)
    
    assert df.shape == (3, 2)
    assert np.isnan(df.at[0, "bar"])
    assert df.at[1, "foo"] == 23
    assert df.at[2, "bar"] == "a"


def test_make_data_frame_2():
    print("Start")
    import django
    from django.db import models
    from libclair.dataframes import make_data_frame
    
    #One can't create models without this
    os.environ['DJANGO_SETTINGS_MODULE'] = 'clairweb.settings'
    django.setup()

    class TestM(models.Model):
        foo = models.FloatField("foo data")
        bar = models.CharField("bar data", max_length=64, 
                               blank=True, default=None)
        #Concrete models must be inside Django-Apps, 
        #therefore this model is abstract.
        class Meta:
            abstract = True
#             app_label = "foo_app"

    df = make_data_frame(TestM, 3)
    df.at[1, "foo"] = 23
    df.at[2, "bar"] = "a"
    print(df)
    print("dtypes:\n", df.dtypes)
    
    assert df.shape == (3, 2)
    assert np.isnan(df.at[0, "bar"])
    assert df.at[1, "foo"] == 23
    assert df.at[2, "bar"] == "a"


def test_convert_model_to_descriptor():
    print("Start")
    import django
    from django.db import models
    from libclair.dataframes import convert_model_to_descriptor
    from libclair.descriptors import TableDescriptor, FieldDescriptor, \
                                     FloatD, StrD
    
    #One can't create models without this
    os.environ['DJANGO_SETTINGS_MODULE'] = 'clairweb.settings'
    django.setup()

    class TestM(models.Model):
        "A test model"
        foo = models.FloatField("foo data")
        bar = models.CharField("bar data", max_length=64, 
                               blank=True, default='')
        #Concrete models must be inside Django-Apps, 
        #therefore this model is abstract.
        class Meta:
            abstract = True
#             app_label = "foo_app"

    td = convert_model_to_descriptor(TestM)
    print(td)
    
    assert isinstance(td, TableDescriptor)
    assert td.name == 'TestM'
    assert td.comment == 'A test model'
    assert len(td.column_descriptors) == 2

    fd = td.column_descriptors[0]
    assert isinstance(fd, FieldDescriptor)
    assert fd.name == 'foo'
    assert fd.data_type is FloatD
    assert fd.default_val == None
    assert fd.comment == 'foo data'

    fd = td.column_descriptors[1]
    assert isinstance(fd, FieldDescriptor)
    assert fd.name == 'bar'
    assert fd.data_type is StrD
    assert fd.default_val == ''
    assert fd.comment == 'bar data'


def test__write_frame__read_frame():
    print("Start")
    import django
#     from django.db import models
    from django.db import utils
    #One can't use models without this
    os.environ['DJANGO_SETTINGS_MODULE'] = 'clairweb.settings'
    django.setup()

    from econdata.models import Listing
    from libclair.dataframes import write_frame_create, read_frame, write_frame
    
    # Create a DataFrame and write it ino the database
    fr1 = pd.DataFrame([{'id':'foo-1', 'site':'a', 'id_site':'1', 'title':'The 1st record.'},
                        {'id':'foo-2', 'site':'a', 'id_site':'2', 'title':'The 2nd record.'}])
    print('\nfr1:\n', fr1)
    write_frame_create(fr1, Listing, delete=True)
    # The records already exist. Creating them again, without deleting them, 
    # must raise an exception.
    with pytest.raises(utils.IntegrityError):
        write_frame_create(fr1, Listing)
    
    # Read the records, that were just created, from the database.
    # Read a few additional empty columns.
    qset = Listing.objects.filter(id__in=['foo-1', 'foo-2'])
    fr2 = read_frame(qset, ['id', 'title', 'time', 'price'])
    print('\nfr2:\n', fr2)
    
    assert pd_types.is_string_dtype(fr2['title'])
    assert pd_types.is_datetime64_any_dtype(fr2['time'])
    assert pd_types.is_numeric_dtype(fr2['price'])
    assert fr2['id'][0] == 'foo-1'
    assert fr2['id'][1] == 'foo-2'
    assert fr2['title'][0] == 'The 1st record.'
    assert fr2['title'][1] == 'The 2nd record.'
    
    # Change the dataframe
    fr2['time'] = [pd.Timestamp('2017-01-01 12:00+0'), 
                   pd.Timestamp('2017-01-02 12:00+0'),]
    fr2['price'] = [101.0, 102.0,]
    print('\nfr2:\n', fr2)
    # Update the records in the database
    write_frame(fr2, Listing)
    
    # Read the updated records from the database.
    qset = Listing.objects.filter(id__in=['foo-1', 'foo-2'])
    fr3 = read_frame(qset, ['id', 'title', 'time', 'price'])
    print('\nfr3:\n', fr3)
    assert_frames_equal(fr2, fr3)



if __name__ == "__main__":
    test_make_data_series_1()
    test_make_data_series_2()
    test_make_data_frame_1()
    test_make_data_frame_2()
    test_convert_model_to_descriptor()
    test__write_frame__read_frame()
    
    pass #IGNORE:W0107
