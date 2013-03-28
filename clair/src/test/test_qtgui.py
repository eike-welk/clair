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
from datetime import datetime

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


def test_ProductEditWidget():
    """Test the ``ProductEditWidget``"""
    from clair.qtgui import ProductEditWidget
    
    print "Start"
    app = QApplication(sys.argv)
    
    view = ProductEditWidget()
    model = create_product_model()
    view.setModel(model)
    
    view.show()
    app.exec_()
    print model.products
    print "End"
    
    
def test_ProductWidget():
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


def test_SearchTaskEditWidget():
    """Test the ``ProductEditWidget``"""
    from clair.qtgui import SearchTaskEditWidget
    
    print "Start"
    app = QApplication(sys.argv)
    
    view = SearchTaskEditWidget()
    model = create_task_model()
    view.setModel(model)
    view.setRow(model.index(1, 0))
    
    view.show()
    app.exec_()
    print model.tasks
    print "End"
    
    
def test_TaskWidget():
    from clair.qtgui import TaskWidget
    
    print "Start"
    app = QApplication(sys.argv)
    
    view = TaskWidget()
    model = create_task_model()
    view.setModel(model)
    
    view.show()
    app.exec_()
    print model.tasks
    print "End"
    

def create_task_model():
    """Create a Qt-model-view model that contains tasks, for testing."""
    from clair.qtgui import TaskModel
    from clair.coredata import SearchTask
    
    tasks = [SearchTask("s-nikon-d90", datetime(2000, 1, 1), "ebay-de", 
                           "Nikon D90", "daily", "100", "150", "300", "EUR", 
                           ["nikon-d90", "nikon-18-105-f/3.5-5.6--1"]),
                SearchTask("s-nikon-d70", datetime(2000, 1, 1), "ebay-de", 
                           "Nikon D70", "daily", "100", "75", "150", "EUR", 
                           ["nikon-d70", "nikon-18-105-f/3.5-5.6--1"]),]
    model = TaskModel()
    model.setTasks(tasks)
    return model
    

def test_TaskModel():
    """
    Test ProductModel, an adapter for a list of ``Product`` objects
    to Qt's model-view architecture.
    """
    model = create_task_model()
    
    #Get table dimensions
    assert model.rowCount() == 2
    assert model.columnCount() == 10
    
    #Get data from model
    index00 = model.createIndex(0, 0)
    id_ = model.data(index00, Qt.DisplayRole)
    assert id_ == "s-nikon-d90"
    id_ = model.data(index00, Qt.EditRole)
    assert id_ == "s-nikon-d90"
    tooltip =  model.data(index00, Qt.ToolTipRole)
    assert isinstance(tooltip, basestring) and len(tooltip) > 0
    
    #Change data in model
    model.setData(index00, "foo", Qt.EditRole)
    #Test if data was really changed
    id_ = model.data(index00, Qt.EditRole)
    assert id_ == "foo"
    
    #Insert 2 rows before line #1 (in the middle)
    model.insertRows(1, 2)
    #Get list of IDs (column 0)
    ids = [model.data(model.createIndex(i, 0), Qt.DisplayRole) 
             for i in range(model.rowCount())]
    assert model.rowCount() == 4
    assert ids == ['foo', u'--', u'--', 's-nikon-d70']
    
    #Remove 2 rows starting at #1
    model.removeRows(1, 2)
    #Get list of product ids (column 1)
    ids = [model.data(model.createIndex(i, 0), Qt.DisplayRole) 
             for i in range(model.rowCount())]
    assert model.rowCount() == 2
    assert ids == ['foo', 's-nikon-d70']
    
    print model.tasks
    print "End"


def test_RadioButtonModel():
    """Test class RadioButtonModel"""
    from clair.qtgui import RadioButtonModel
    csr =  Qt.CheckStateRole
    
    mo = RadioButtonModel(3, 2, [3, 4])
    
    mo.setValues([[False, False, False, "one", "two"]])
    
    #Test size
    assert mo.columnCount() == 5
    assert mo.rowCount() == 1
    
    i00 = mo.index(0, 0)
    i01 = mo.index(0, 1)
    i02 = mo.index(0, 2)
    i03 = mo.index(0, 3)
    i04 = mo.index(0, 4)
    
    #Test the radio button aspect
    #Set field [0,0] to True
    mo.setData(i00, True)
    assert all([mo.data(i00, csr), not mo.data(i01, csr), not mo.data(i02, csr)])
    #Set field [0,1] to True. field [0,0] must become False automatically
    mo.setData(i01, True)
    assert all([not mo.data(i00, csr), mo.data(i01, csr), not mo.data(i02, csr)])
    #Set field [0,2] to True. other fields] must become False automatically
    mo.setData(i02, True)
    assert all([not mo.data(i00, csr), not mo.data(i01, csr), mo.data(i02, csr)])
    
    #Test regular fields
    mo.setData(i03, "Foo")
    mo.setData(i04, "Bar")
    assert mo.data(i03) == "Foo" and mo.data(i04) == "Bar"
    mo.setData(i03, "Boo")
    mo.setData(i04, "Baz")
    assert mo.data(i03) == "Boo" and mo.data(i04) == "Baz"
    
    #Test adding and deleting lines
    mo.insertRows(0, 2)
    assert mo.rowCount() == 3
    assert mo.data(mo.index(2, 3)) == "Boo"
    mo.removeRows(0, 2)
    assert mo.rowCount() == 1
    assert mo.data(mo.index(0, 3)) == "Boo"
    
    print "finished successfully."
    
    
def test_LearnDataProxyModel():
    """Test class RadioButtonModel"""
    from clair.qtgui import LearnDataProxyModel, ListingsModel
    from clair.coredata import make_listing_frame
    csr =  Qt.CheckStateRole

    
    #Create test data
    listings = make_listing_frame(1)
    #Product "foo" is present, "bar" absent, nothing is known about "baz" 
    listings["expected_products"][0] = ["foo", "bar", "baz"]
    listings["products"][0]         = ["foo"]
    listings["products_absent"][0]   = ["bar"]
    #Create listings model that we can adapt
    lsmod = ListingsModel()
    lsmod.setListings(listings)
    
    
    mo = LearnDataProxyModel()
    mo.setSourceModel(lsmod, 3, 4, 5)
    mo.setRow(lsmod.index(0, 0))
    
    print mo.values
    
    #Test size
    assert mo.columnCount() == 4
    assert mo.rowCount() == 4    #includes additional empty row
    
    #Test data conversion
    #1st row: [True, False, "foo", ...]
    assert bool(mo.data(mo.index(0, 0), csr)) == True
    assert bool(mo.data(mo.index(0, 1), csr)) == False
    assert mo.data(mo.index(0, 2)) == "foo"
    #2nd row: [False, True, "bar", ...]
    assert bool(mo.data(mo.index(1, 0), csr)) == False
    assert bool(mo.data(mo.index(1, 1), csr)) == True
    assert mo.data(mo.index(1, 2)) == "bar"
    #3rd row: [False, False, "baz", ...]
    assert bool(mo.data(mo.index(2, 0), csr)) == False
    assert bool(mo.data(mo.index(2, 1), csr)) == False
    assert mo.data(mo.index(2, 2)) == "baz"
    
    #Change the data
    mo.setData(mo.index(0, 0), False, csr)
    mo.setData(mo.index(1, 0), True, csr)
    mo.setData(mo.index(2, 1), True, csr)
    
    #Test conversion back to internal format
    assert listings["expected_products"][0] == ["foo", "bar", "baz"]
    assert listings["products"][0]          == ["bar"]
    assert listings["products_absent"][0]   == ["baz"]
    
    print "finished successfully."
    

def test_LearnDataProxyModel_GUI():
    """Test class RadioButtonModel"""
    from clair.qtgui import LearnDataProxyModel, ListingsModel
    from clair.coredata import make_listing_frame
    
    print "Start"
    app = QApplication(sys.argv)
    
    #Create test data
    listings = make_listing_frame(1)
    #Product "foo" is present, "bar" absent, nothing is known about "baz" 
    listings["expected_products"][0] = ["foo", "bar", "baz"]
    listings["products"][0]         = ["foo"]
    listings["products_absent"][0]   = ["bar"]
    #Create listings model that we can adapt
    lsmod = ListingsModel()
    lsmod.setListings(listings)
    
    
    mo = LearnDataProxyModel()
    mo.setSourceModel(lsmod, 3, 4, 5)
    mo.setRow(lsmod.index(0, 0))

    view = QTreeView()
    view.setModel(mo)
    
    view.show()
    app.exec_()
    
    print mo.values
    print "expectedProducts:", listings["expected_products"][0]
    print "products:        ", listings["products"][0]
    print "productsAbsent:  ", listings["products_absent"][0]
    
    print "End"
    

def test_DataWidgetHtmlView():
    """Test ListingsEditWidget, which displays a DataFrame of listings."""
    from clair.qtgui import DataWidgetHtmlView
    
    print "Start"
    app = QApplication(sys.argv)
    
    view = DataWidgetHtmlView()
    view.setHtml("Baz buz <b>Fooo</b> bar.")
    view.setTabContents(1)
    view.setTabContents(2)
    view.setTabContents(0)
    
    view.show()
    app.exec_()
    
    print "End"


def test_ListingsEditWidget():
    """Test ListingsEditWidget, which displays a single listing."""
    from clair.qtgui import ListingsEditWidget, ListingsModel
    from clair.coredata import make_listing_frame
    
    print "Start"
    app = QApplication(sys.argv)
    
    listings = make_listing_frame(4)
    model = ListingsModel()
    model.setListings(listings)
    view = ListingsEditWidget()
    view.setModel(model)
    view.setRow(model.index(1, 0))
    
    view.show()
    app.exec_()
    print "End"


def test_ListingsWidget():
    """Test ListingsWidget, which displays a DataFrame of listings."""
    from clair.qtgui import ListingsWidget, ListingsModel
    from clair.coredata import make_listing_frame
    
    print "Start"
    app = QApplication(sys.argv)
    
    listings = make_listing_frame(4)
    model = ListingsModel()
    model.setListings(listings)
    view = ListingsWidget()
    view.setModel(model) 
    
    view.show()
    app.exec_()
    print "End"

    
def test_ListingsModel():
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
    assert data == "None"
    #Change data in model
    model.setData(index17, "foo", Qt.EditRole)
    #Test if data was really changed
    data = model.data(index17, Qt.EditRole)
    assert data == "foo"
    #Try to get data in edit role
    data = model.data(index17, Qt.EditRole)
    assert data == "foo"
    
    print listings
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
#    test_ProductEditWidget()
#    test_ProductWidget()
#    test_ProductModel()
#    test_SearchTaskEditWidget()
#    test_TaskWidget()
#    test_TaskModel()
#    test_RadioButtonModel()
#    test_LearnDataProxyModel()
#    test_LearnDataProxyModel_GUI()
#    test_DataWidgetHtmlView()
#    test_ListingsEditWidget()
#    test_ListingsWidget()
#    test_ListingsModel()
    test_GuiMain()
    
#    experiment_qt()
    
    pass #IGNORE:W0107
    
