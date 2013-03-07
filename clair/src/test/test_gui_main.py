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

#Switch PyQt to API version 2
import sip
sip.setapi("QData", 2)
sip.setapi("QDateTime", 2)
sip.setapi("QString", 2)
sip.setapi("QTextStream", 2)
sip.setapi("QTime", 2)
sip.setapi("QUrl", 2)
sip.setapi("QVariant", 2)
#Import PyQt after version change.

import sys
import os
import os.path as path
import time
import logging

import pandas as pd

from PyQt4.QtGui import QApplication, QTreeView, QTableView, QSplitter

#Setup logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime



def relative(*path_components):
    "Create file a path that is relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_components))


def test_ProductWidget():
    from clair.gui_main import ProductWidget
    from clair.coredata import Product
    
    def slot_contents_changed():
        print "contents changed"
        
    prod = Product("nikon-d90", "Nikon D90", "Nikon D90 DSLR camera.", 
                   ["Nikon", "D 90"], ["photo.system.nikon.camera",
                                       "photo.camera.system.nikon"])
        
    app = QApplication(sys.argv)
    pw = ProductWidget()
    #TODO: create model and test widget with it.
    pw.show()
    app.exec_()
    
    print "End"
    
    
@pytest.mark.skipif("True") #IGNORE:E1101
def test_ProductModel():
    from clair.gui_main import ProductModel, ProductWidget
    from clair.coredata import Product
    
    print "Start"
    app = QApplication(sys.argv)
    
    products = [Product("nikon-d90", "Nikon D90", "Nikon D90 DSLR camera.", 
                        ["Nikon", "D 90"], ["photo.system.nikon.camera",
                                            "photo.camera.system.nikon"]),
                Product("nikon-d70", "Nikon D70", "Nikon D70 DSLR camera.", 
                        ["Nikon", "D 70"], ["photo.system.nikon.camera",
                                            "photo.camera.system.nikon"])]
    
    model = ProductModel()
    model.setProducts(products)
    #TODO: test adding and removing rows
    #TODO: sorting with QSortFilterProxyModel
    
    view = QTreeView()
    view.setModel(model)
    view.setDragEnabled(True)
    view.setAcceptDrops(True)
    view.setDropIndicatorShown(True)
    
    prodw = ProductWidget()
    prodw.set_model(model)
    
    split = QSplitter()
    split.addWidget(view)
    split.addWidget(prodw)
    split.show()
    app.exec_()
    
#    view = QTableView()
#    view.setModel(model)
#    view.show()
#    app.exec_()
    
    print model.products
    print "End"

 
def experiment_qt():    
    print "Start"
    app = QApplication(sys.argv)
    view = QTreeView()
    view.show()
    app.exec_()
    print "End"
    
    
if __name__ == '__main__':
#    test_ProductWidget()
    test_ProductModel()
    
#    experiment_qt()
    
    pass
    