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

from PyQt4.QtGui import QApplication, QTreeView
from PyQt4.QtCore import Qt, QModelIndex

#Setup logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime



def relative(*path_components):
    "Create file a path that is relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_components))


def test_ProductWidget():
    """Test the ``ProductWidget``"""
    from clair.qtgui import ProductWidget
    
    print "Start"
    app = QApplication(sys.argv)
    
    view = ProductWidget()
    model = create_product_model()
    view.setModel(model)
    
    view.show()
    app.exec_()
    print model.products
    print "End"
    
    
def test_ProductListWidget():
    from clair.qtgui import ProductListWidget
    
    print "Start"
    app = QApplication(sys.argv)
    
    view = ProductListWidget()
    model = create_product_model()
    view.setModel(model)
    
    view.show()
    app.exec_()
    print model.products
    print "End"
    

def create_product_model():
    """Create a Qt-model-view model that contains products, for testing."""
    from clair.qtgui import ProductModel
    from clair.coredata import Product
    
    products = [Product("nikon-d90", "Nikon D90", "Nikon D90 DSLR camera.", 
                        ["Nikon", "D 90"], ["photo.system.nikon.camera",
                                            "photo.camera.system.nikon"]),
                Product("nikon-d70", "Nikon D70", "Nikon D70 DSLR camera.", 
                        ["Nikon", "D 70"], ["photo.system.nikon.camera",
                                            "photo.camera.system.nikon"])]
    model = ProductModel()
    model.setProducts(products)
    return model
    

def test_ProductModel():
    """
    Test ProductModel, an adapter for a list of ``Product`` objects
    to Qt's model-view architecture.
    """
    model = create_product_model()
    
    #Get table dimensions
    assert model.rowCount() == 2
    assert model.columnCount() == 5
    
    #Get data from model
    index01 = model.createIndex(0, 1)
    name = model.data(index01, Qt.DisplayRole)
    assert name == "Nikon D90"
    name = model.data(index01, Qt.EditRole)
    assert name == "Nikon D90"
    tooltip =  model.data(index01, Qt.ToolTipRole)
    assert isinstance(tooltip, basestring) and len(tooltip) > 0
    
    #Change data in model
    model.setData(index01, "foo", Qt.EditRole)
    #Test if data was really changed
    name = model.data(index01, Qt.EditRole)
    assert name == "foo"
    
    #Insert 2 rows before line #1 (in the middle)
    model.insertRows(1, 2)
    #Get list of product names (column 1)
    names = [model.data(model.createIndex(i, 1), Qt.DisplayRole) 
             for i in range(model.rowCount())]
    assert model.rowCount() == 4
    assert names == ['foo', u'', u'', 'Nikon D70']
    
    #Remove 2 rows starting at #1
    model.removeRows(1, 2)
    #Get list of product names (column 1)
    names = [model.data(model.createIndex(i, 1), Qt.DisplayRole) 
             for i in range(model.rowCount())]
    assert model.rowCount() == 2
    assert names == ['foo', 'Nikon D70']
    
    print model.products
    print "End"


def test_ListingsListWidget():
    """Test ListingsListWidget, which displays a DataFrame of listings."""
    from clair.qtgui import ListingsListWidget, ListingsModel
    from clair.coredata import make_listing_frame
    
    print "Start"
    app = QApplication(sys.argv)
    
    listings = make_listing_frame(4)
    model = ListingsModel()
    model.setListings(listings)
    view = ListingsListWidget()
    view.setModel(model) 
    
    view.show()
    app.exec_()
    print "End"

    
def test_ListingModel():
    """Test ListingsModel"""
    from clair.coredata import make_listing_frame
    from clair.qtgui import ListingsModel
    
    listings = make_listing_frame(4)
    
    model = ListingsModel()
    model.setListings(listings)
    
    #Get table dimensions
    assert model.rowCount() == 4
    assert model.columnCount() == len(listings.columns)
    
    #Get data from model - Currently it contains only None and nan
    index17 = model.createIndex(1, 7)
    data = model.data(index17, Qt.DisplayRole)
    assert data == None
    #Change data in model
    model.setData(index17, "foo", Qt.EditRole)
    #Test if data was really changed
    data = model.data(index17, Qt.EditRole)
    assert data == "foo"
    #Try to get data in edit role
    data = model.data(index17, Qt.EditRole)
    assert data == "foo"
    
    print listings.icol(7)
    
    
def test_GuiMain():
    """Test the regular run of the GUI application"""
    from clair.qtgui import GuiMain
    
    print "start"
    GuiMain.application_main()
    print "finished"
    
 
def experiment_qt():
    """Template for functions that test Qt GUI components."""
    print "Start"
    app = QApplication(sys.argv)
    view = QTreeView()
    view.show()
    app.exec_()
    print "End"
    
    
if __name__ == '__main__':
#    test_ProductWidget()
#    test_ProductListWidget()
#    test_ProductModel()
#    test_ListingsListWidget()
#    test_ListingModel()
    test_GuiMain()
    
#    experiment_qt()
    
    pass #IGNORE:W0107
    