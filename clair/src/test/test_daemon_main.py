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


def relative(*path_components):
    "Create file a path that is relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_components))


def test_perform_tasks():
    from clair.daemon_main import MainObj
    from clair.coredata import Product, SearchTask, UpdateTask

    conf_dir = relative("..")
    data_dir = None
    
    m = MainObj(conf_dir, data_dir)
    m.add_products([Product("nikon-d90", "Nikon D90", "DSLR Camera", 
                            None, None),
                    Product("nikon-d70", "Nikon D70", "DSLR Camera", 
                            None, None)])
    m.add_tasks([SearchTask("nikon-d90", datetime(2000,1,1), "Ebay-DE", None, 
                            "Nikon D90", 5, 10, 500, "EUR", ["nikon-d90"]),
                 SearchTask("nikon-d70", datetime(2000,1,1), "Ebay-DE", None, 
                            "Nikon D70", 5, 10, 500, "EUR", ["nikon-d70"])])
    
    m.perform_tasks()
    print m.tasks
    print m.listings[["title", "price", "sold", "time"]].to_string()
    
    upd_listings = m.listings["id"]
    m.add_tasks([UpdateTask("update-1", datetime(2000,1,1), "Ebay-DE", None, 
                           upd_listings)])    
    m.perform_tasks()
    print m.tasks
    print m.listings[["title", "price", "sold", "time"]].to_string()
    print "finished!"
    
    
    
if __name__ == "__main__":
    test_perform_tasks()
    
    pass
