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
Library for creating diagrams.
"""

from __future__ import division
from __future__ import absolute_import              

import numpy as np
import pandas as pd



class Filter(object):
    """
    Base class of filters to select interesting rows (listings or prices) 
    from a (moderately sized) ``DataFrame``. They are useful for creating
    diagrams.
    """
    def filter(self, in_frame):
        """
        Select the interesting rows from the input ``DataFrame``.
        
        Returns ``DataFrame`` that only contains the interesting rows.
        """
        raise NotImplementedError()
    
    

class FilterInterval(Filter):
    """
    Select rows in a ``DataFrame`` based on a half open interval.
    """
    def __init__(self, column, intv_start, intv_stop, inside=True):
        super(FilterInterval, self).__init__()
        assert isinstance(column, basestring), \
               "Column name must be string or unicode."
        assert isinstance(inside, bool), \
               "Parameter ``inside`` must be ``bool``."
        msg_bounds = "Start and stop of the interval must be similar " \
                     "to numbers, and have comparison operators."
        assert hasattr(intv_start, "__lt__") or \
               hasattr(intv_start, "__cmp__"), msg_bounds
        assert hasattr(intv_stop, "__lt__") or \
               hasattr(intv_stop, "__cmp__"), msg_bounds
        self.column = column
        self.intv_start = intv_start
        self.intv_stop = intv_stop
        self.inside = inside

    def filter(self, in_frame):
        """
        Select the interesting rows from the input ``DataFrame``.
        
        Returns ``DataFrame`` that only contains the interesting rows.
        """
        assert isinstance(in_frame, pd.DataFrame)
        col = in_frame[self.column]
        if self.inside:
            where = (col >= self.intv_start) & (col < self.intv_stop)
        else:
            where = (col < self.intv_start) | (col >= self.intv_stop)
            
        res_rows = in_frame.ix[where]
        return res_rows
    


class FilterContains(Filter):
    """
    Select rows in a ``DataFrame`` if a field contains a certain string.
    """
    def __init__(self, column, search_word, is_string=False):
        super(FilterContains, self).__init__()
        assert isinstance(column, basestring), \
               "Column name must be string or unicode."
        assert isinstance(search_word, basestring), \
               "Parameter ``search_word`` name must be string or unicode."
        assert isinstance(is_string, bool), \
               "Parameter ``is_string`` must be ``bool``."
        self.column = column
        self.search_word = search_word
        self.is_string = is_string
        
    def filter(self, in_frame):
        """
        Select the interesting rows from the input ``DataFrame``.
        
        Returns ``DataFrame`` that only contains the interesting rows.
        """
        assert isinstance(in_frame, pd.DataFrame)
        col = in_frame[self.column]
        where = np.zeros((len(col),), dtype=bool)
        if self.is_string:
            #Convert all elements of ``col`` to strings and 
            #do a string search for the search word
            #TODO: vectorized string operations
            col = col.apply(unicode)
            for i, s in enumerate(col):
                if s.find(self.search_word) >= 0:
                    where[i] = True
        else:
            #Consider all elements of col to be containers (eg. list, set)
            #Test if search word is in container.
            isnull = col.isnull()
            for i in range(len(col)):
                if isnull[i]:
                    continue
                if self.search_word in col.iget(i):
                    where[i] = True
        
        res_rows = in_frame.ix[where]
        return res_rows

