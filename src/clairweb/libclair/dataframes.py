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
Functions that create ``pandas.DataFrame`` objects.

A ``DataFrame`` is a 2-dimensional table.  Each column has a *name* and each row
has an *index*. The elements of a column all have the same data type. A row can
contain elements of diffentent types.

A ``DataFrame`` can repesent a table from the database in the comuter's RAM.
Algorithms that involve multiple rows of a table are implemented with
``DataFrame`` objects.
"""

import numpy as np
import pandas  as pd
from django.db import models, transaction
# from django.db.models import QuerySet
# from django.db import models.query.QuerySet

from libclair import descriptors 



def convert_model_to_descriptor(dj_model):
    """
    Convert a Django database model into an equivalent Clair descriptor.
    """
    assert issubclass(dj_model, models.Model)
    
    all_fields = dj_model._meta.get_fields()
    fields = [_convert_field_to_descriptor(f) for f in all_fields
              if f.auto_created == False]

    return descriptors.TableDescriptor(dj_model.__name__, 
                                       '0', 
                                       dj_model.__name__ + '.json', 
                                       dj_model.__doc__ if dj_model.__doc__ is not None else '', 
                                       fields)

def _convert_field_to_descriptor(dj_field):
    """
    Convert a Django database field to an equivalent Clair descriptor.
    """
    assert isinstance(dj_field, models.Field)
    
    type_trans = {
        models.CharField: descriptors.StrD,
        models.URLField: descriptors.StrD,
        models.FloatField: descriptors.FloatD,
        models.IntegerField: descriptors.IntD,
        models.BooleanField: descriptors.BoolD,
        models.NullBooleanField: descriptors.BoolD,
        models.DateField: descriptors.DateTimeD,
        models.DateTimeField: descriptors.DateTimeD,
        }
    
    cl_type = type_trans[type(dj_field)]
    return descriptors.FieldDescriptor(str(dj_field.name), 
                                       cl_type, 
                                       dj_field.get_default(), 
                                       dj_field.verbose_name)


def make_data_series(descr, nrows=None, index=None):
    """
    Create an empty ``pandas.Series``. 
    
    Parameters
    ----------
    
    descr: ``descriptors.FieldDescriptor``, ``models.Field``
        Description of data type and default value
        of the stored data.
        
    nrows: ``int``
        Number of elements in the new ``pandas.Series`` object.
        
    index: ``list``, ``pandas.Index``
        The index of the new series. Basically a list of primary keys.

        If this argument is omitted or ``None``, a sequence of integers 
        (``range(nrows)``) is used as index labels.
    """
    assert isinstance(descr, (descriptors.FieldDescriptor, models.Field))
    assert nrows is not None or index is not None, \
           "Either ``nrows`` or ``index`` must be specified."

    if isinstance(descr, models.Field):
        descr = _convert_field_to_descriptor(descr)
    
    #Create the index if it is not given.
    if index is None:
        index=list(range(nrows))
    if nrows is not None:
        assert nrows == len(index), "Inconsistent arguments"

    default_val = descr.default_val
    
    if descr.data_type == descriptors.DateTimeD:
        temp = pd.Series(data=default_val, index=index, dtype=pd.Timestamp)
        return pd.to_datetime(temp)
        
    if   descr.data_type == descriptors.BoolD:
        dtype = object
    elif descr.data_type == descriptors.IntD:
        dtype = np.int32
    elif descr.data_type == descriptors.FloatD:
        dtype = np.float64
    else:
        dtype = object
    return pd.Series(data=default_val, index=index, dtype=dtype)


def make_data_frame(descr, nrows=None, index=None):
    """
    Create an empty ``pandas.DataFrame`` as specified by ``descr``. 
    
    Column labels, data types, and default values are taken from ``descr``.
    The object contains no data, all values are ``nan`` or the column's 
    default values.
    
    Arguments ``nrows`` and ``index`` both are optional, 
    but one of them must be given. 
    If both arguments are given they must be consistent.
    
    Arguments
    ---------
    
    descr : TableDescriptor or Django model class
        Contains column labels, data types, and default values.
        
    nrows : int 
        Number of rows.
        
    index : iterable 
        The index labels (primary keys) of the new data frame. 
        
        If this argument is omitted or ``None``, a sequence of integers 
        (``range(nrows)``) is used as index labels.
    """
    assert isinstance(descr, descriptors.TableDescriptor) or \
           issubclass(descr, models.Model)
    assert nrows is not None or index is not None, \
           "Either ``nrows`` or ``index`` must be specified."
    
    if isinstance(descr, type) and issubclass(descr, models.Model):
        descr = convert_model_to_descriptor(descr)
           
    if index is None:
        index=list(range(nrows))
    if nrows is not None:
        assert nrows == len(index), "Inconsistent arguments"
    
    dframe = pd.DataFrame(index=index)
    for fieldD in descr.column_descriptors:
        col = make_data_series(fieldD, index=index)
        dframe[fieldD.name] = col
        
    return dframe


def write_frame_create(pd_frame, db_model, fieldnames=None, delete=False):
    """
    Write a Pandas ``DataFrame`` into Django's database, as new records.
    
    The alorithm creates new records in the database, and if desired deletes 
    already existing records. Deleting existing records will destroy foreign
    key relations, if the database is not specifically designed for it. 
    
    Columns that are not in the database are ignored.
    
    The fastest way to write new records into the database.
    """
    assert isinstance(pd_frame, pd.DataFrame)
    assert issubclass(db_model, models.Model)
    assert isinstance(fieldnames, (set, list, tuple, type(None)))
    
    # If no field names given, try to write all of the frame's columns
    if fieldnames is None:
        fieldnames = set(pd_frame.columns.values.tolist())
    else:
        fieldnames = set(fieldnames)
    
    # Drop all columns that have no correspondig field in the database
    db_all_fields = db_model._meta.get_fields()
    db_fieldnames = set([f.name for f in db_all_fields
                         if f.auto_created == False])
    wr_fieldnames=fieldnames.intersection(db_fieldnames)
    wr_frame = pd_frame[list(wr_fieldnames)]

    with transaction.atomic():
        # Delete all records that are already in the database
        # If no ID-field is written, assume ID is automatically incremented,
        # and don't delete anything.
        if delete:
            id_name = db_model._meta.pk.name
            if id_name in wr_fieldnames:
                delete_ids = list(wr_frame[id_name])
                # Programatically create argument like: ``.filter(id__in=delete_ids)``
                delete_kwargs = {id_name + '__in': delete_ids}
                db_model.objects.filter(**delete_kwargs).delete()

        # Create the rows in the DataFrame as new records in the database.
        rows = []
        for i in range(len(wr_frame)):
            kwargs = dict(wr_frame.iloc[i])
            rows.append(db_model(**kwargs))
        db_model.objects.bulk_create(rows)


def write_frame(pd_frame, db_model, fieldnames=None):
    """
    Write a Pandas ``DataFrame`` into Django's database.
    
    The alorithm updates existing records, or creates new records if necesary.
    Columns that are not in the database table are ignored.
    """
    assert isinstance(pd_frame, pd.DataFrame)
    assert issubclass(db_model, models.Model)
    assert isinstance(fieldnames, (set, list, tuple, type(None)))
    
    # If no field names given, try to write all of the frame's columns
    if fieldnames is None:
        fieldnames = set(pd_frame.columns.values.tolist())
    else:
        fieldnames = set(fieldnames)
    
    if 'defaults' in fieldnames:
        raise KeyError('Column name "defaults" is illegal in this algorithm.')
    
    # Drop all columns that have no correspondig field in the database
    db_all_fields = db_model._meta.get_fields()
    db_fieldnames = set([f.name for f in db_all_fields
                         if f.auto_created == False])
    wr_fieldnames=fieldnames.intersection(db_fieldnames)
    wr_frame = pd_frame[list(wr_fieldnames)]

    id_name = db_model._meta.pk.name
    if id_name not in wr_fieldnames:
        raise KeyError('Argument ``pd_frame``: Missing column "{id_name}". '
                       'The DataFrame must contain a column for the primary key.'
                       .format(id_name=id_name))
    
    with transaction.atomic():
        for i in range(len(wr_frame)):
            record = wr_frame.iloc[i]
            kwargs = {id_name: record[id_name],
                      'defaults': dict(record)}
            db_model.objects.update_or_create(**kwargs)


def read_frame(queryset, fieldnames=None):
    """
    Read subset of a database table from the Database.
    """
    assert isinstance(queryset, models.QuerySet)
    assert isinstance(fieldnames, (list, tuple, type(None)))

    all_fields = queryset.model._meta.get_fields()
    if fieldnames is None:
        fields = [f for f in all_fields if f.auto_created == False]
        fieldnames = [f.name for f in fields]
    else:
        fields = [f for f in all_fields if f.auto_created == False and f.name in fieldnames]
        fieldnames = list(fieldnames)

    # Get data from database and construct the dataframe.
    vals = list(queryset.values_list(*fieldnames))
    frame = pd.DataFrame(vals, columns=fieldnames)

    # Convert date and time fields to ``datetime64`` even in edge cases.
    for field in fields:
        if isinstance(field, (models.DateField, models.DateTimeField)):
            frame[field.name] = pd.to_datetime(frame[field.name])
        elif isinstance(field, (models.FloatField)):
            frame[field.name] = frame[field.name].astype(np.float64)
        elif isinstance(field, (models.IntegerField)):
            frame[field.name] = frame[field.name].astype(np.int64)
        
    return frame

