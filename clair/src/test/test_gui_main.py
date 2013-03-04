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
Test the deamon's top level object.
"""

from __future__ import division
from __future__ import absolute_import  
            
import pytest #contains `skip`, `fail`, `raises`, `config`

import sys
import os
import os.path as path
import time
import logging

import pandas as pd

from clair.gui_main import ProductWidget, ProductController
from clair.coredata import Product

from PyQt4 import QtGui, QtCore


#Setup logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime



def relative(*path_components):
    "Create file a path that is relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_components))


def test_ProductWidget():
    print "Start"
    
    def slot_contents_changed():
        print "contents changed"
        
    prod = Product("nikon-d90", "Nikon D90", "Nikon D90 DSLR camera.", 
                    ["Nikon", "D 90"], ["photo.camera.system.nikon",
                                        "photo.system.nikon.camera"])
        
    app = QtGui.QApplication(sys.argv)
    pw = ProductWidget()
    
    #Test setting getting the data before it can be changed interactively
    pw.set_contents(prod)
    prod1 = pw.get_contents()
    assert prod == prod1
    
    pw.contents_changed.connect(slot_contents_changed)
    pw.show()
    app.exec_()
    
    print pw.get_contents()
    print "End"
    
    
if __name__ == '__main__':
    test_ProductWidget()
    
#    experiment_qt()
    
    pass
    