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

# import os
# import os.path as path
# import glob
#import string
# from datetime import datetime #, timedelta
# import logging

# import dateutil
# from numpy import nan, isnan #IGNORE:E0611
import pandas as pd

from clair.descriptors import TableDescriptor

"""

"""

class JsonWriter(object):
    """
    Convert DataFrame objects to JSON, and write them to disk.
    """
    def __init__(self, descriptor):
        assert isinstance(descriptor, TableDescriptor)
        self.descriptor = descriptor
        
    def _convert_to_dict(self, frame):
        """
        Convert a dataframe to a nested `dict`. 
        
        Columns that are not in the `TableDescriptor` are removed.
        The dict contains additional metadata from the `TableDescriptor`.
        """
        assert isinstance(frame, pd.DataFrame)
        
        # TODO: Test if column in dataframe have the right type
        # TODO: convert dates and times
        
        # Remove columns that are not in descriptor.
        frame = frame.copy(deep=False)
        legalCols = {col.name for col in self.descriptor.column_descriptors}
        for cname in frame.columns:
            if cname not in legalCols:
                del frame[cname]
        
        frame_rows = frame.to_dict(orient='records')
        out_dict = {'1_header' : 
                       {'name': self.descriptor.name, 
                        'version': self.descriptor.version,
                        'comment': self.descriptor.comment},
                    '2_rows': frame_rows}
        return out_dict
    
    # The interface -----------------------------------------------------------
    def dump(self, frame, file_object):
        pass
        
    def load(self, file_object):
        pass
