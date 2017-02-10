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
Input and Output of Data in JSON Format
=======================================

Structure of DataFrame -> JSON conversion
-----------------------------------------
   
* Split DataFrame into fragments that are saved separately
    * Done by upper level object
* Test if given DataFrame conforms to descriptor
* Convert descriptor to dict
* Convert DataFrame to dict
* Assemble complete dict that contains DataFrame and header
* Convert dict to JSON and write it to a temporary file
* Rename the temporary file.
    * Done by upper level object
   
Loading and saving series of files
----------------------------------
   
Loading and saving series of files is done by an upper level object,
that can be used for all file formats.
"""

# import logging
import json
import pandas as pd

from clair.descriptors import TableDescriptor, DateTimeD
from clair.dataframes import make_data_series


class JsonWriter(object):
    """
    Convert `DataFrame` objects to/from JSON. 
    Reads and writes to/from file objects.
    
    TODO: Test if columns in dataframe have the right type
    """
    def __init__(self, descriptor):
        assert isinstance(descriptor, TableDescriptor)
        self.descriptor = descriptor
        
    # The interface -----------------------------------------------------------
    
    def dump(self, frame, file_object):
        """
        Write the `DataFrame` to a file object in JSON format.
        
        This function does not close the file object.
        """        
        tmp_dict = self._convert_frame_to_dict(frame)
        json.dump(tmp_dict, file_object, sort_keys=True, indent=2, ensure_ascii=False, check_circular=False)
        
    def load(self, file_object):
        tmp_dict = json.load(file_object)
        return self._convert_dict_to_frame(tmp_dict)
    
    def _convert_frame_to_dict(self, frame):
        """
        Convert a `DataFrame` to a nested `dict`.
        
        The `dict` can be directly fed to the JSON writer.
        
        Columns that are not in the `TableDescriptor` are removed.
        The dict contains additional metadata from the `TableDescriptor`.
        """
        assert isinstance(frame, pd.DataFrame)
        
        frame = frame.copy(deep=False)
        legalCols = {col.name: col for col in self.descriptor.column_descriptors}
        for cname in frame.columns:
            # Remove columns that are not in descriptor.
            if cname not in legalCols:
                #TODO: use logging instead
                print('Illegal column: ', cname)
                del frame[cname]
                continue
            # Convert datetime to string
            if legalCols[cname].data_type == DateTimeD:
                frame[cname] = frame[cname].apply(str)
        
        frame_rows = frame.to_dict(orient='records')
        out_dict = {'1_header' : 
                       {'name': self.descriptor.name, 
                        'version': self.descriptor.version,
                        'comment': self.descriptor.comment},
                    '2_rows': frame_rows}
        return out_dict
    
    def _convert_dict_to_frame(self, in_dict):
        """
        Convert a nested `dict` to a `DataFrame`.
        
        Warns if additional columns are present, that are not in the 
        `TableDescriptor`. Their contents is ignored.
        
        Warns if columns are absent. They are created empty.
        """
        assert isinstance(in_dict, dict)
        
        assert in_dict['1_header']['name'] == self.descriptor.name
        assert in_dict['1_header']['version'] == self.descriptor.version
        assert isinstance(in_dict['2_rows'], list)
        
        tmp_frame = pd.DataFrame.from_dict(in_dict['2_rows'])
        frame = pd.DataFrame()
        for col_desc in self.descriptor.column_descriptors:
            cname = col_desc.name
            if cname not in tmp_frame.columns:
                # TODO: use logging instead
                print('Missing column: ', cname)
                frame[cname] = make_data_series(col_desc, tmp_frame.shape[0])
                continue
            else:
                frame[cname] = tmp_frame[cname]
            
            # Convert string to datetime where needed
            if col_desc.data_type == DateTimeD:
                frame[cname] = pd.to_datetime(frame[cname])
            
        # Search for illegal columns
        legalCols = {col.name for col in self.descriptor.column_descriptors}
        for cname in tmp_frame.columns:        
            if cname not in legalCols:
                # TODO: use logging instead
                print('Additional column: ', cname)
                continue
    
        return frame

    
