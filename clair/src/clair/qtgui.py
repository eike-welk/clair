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
Main module for the graphical user interface.
"""

from __future__ import division
from __future__ import absolute_import              

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
from datetime import datetime
import logging
import time

import dateutil
from numpy import isnan
import pandas as pd
from PyQt4.QtCore import (Qt, pyqtSignal, pyqtProperty, QModelIndex,
                          QAbstractItemModel, QAbstractTableModel, 
                          QSettings, QCoreApplication, QVariant,)
from PyQt4.QtGui import (QWidget, QLabel, QPushButton, QLineEdit, QTextEdit, 
                         QSplitter, QMainWindow, QTabWidget, QCheckBox, 
                         QComboBox, QGroupBox, 
                         QFileDialog, QMessageBox, QProgressDialog,
                         QApplication, 
                         QGridLayout, QTreeView, QAbstractItemView, QAction,
                         QDataWidgetMapper, QSortFilterProxyModel, QKeySequence,
                         QItemSelectionModel, QItemEditorCreatorBase, QFont,
                         QStyledItemDelegate, QItemEditorFactory,)
from PyQt4.QtWebKit import QWebView

from clair.coredata import make_listing_frame, Product, SearchTask, DataStore
from clair.textprocessing import HtmlTool, RecognizerController



def QtLoadUI(uifile):
    from PyQt4 import uic
    return uic.loadUi(uifile)



def to_text_time(time):
    """Convert ``datetime`` to text in safe way."""
    try:
        return time.isoformat(" ")
    except ValueError:
        return "Date Error: " + repr(time)
    
    
    
class RecognizerWidget(QWidget):
    """
    Manipulate a single product recognizer
    """
    def __init__(self):
        super(RecognizerWidget, self).__init__()
        
        #Transfers data between model and widgets
        self.mapper = QDataWidgetMapper()
        #Stores the product recognition algorithms.
        self.recognizers = RecognizerController() #Dummy
        #Stores all important data of the application
        self.data = DataStore() #Dummy
        
        self.v_id = QLabel()
        
        l_id = QLabel("ID")
        
        b_train_curr = QPushButton("&Train Recognizer")
        b_train_all = QPushButton("Train &All Recognizers")
        b_validate = QPushButton("Validate Recognizer")
        b_test = QPushButton("&Test Recognizer")
        b_run = QPushButton("&Run Recognizers")
        
        grid = QGridLayout()
        grid.addWidget(l_id,               0, 0)
        grid.addWidget(self.v_id,          0, 1, 1, 2)
        grid.addWidget(b_train_curr,       1, 0)
        grid.addWidget(b_train_all,        1, 1)
        grid.addWidget(b_validate,         2, 0)
        grid.addWidget(b_test,             2, 1)
        grid.addWidget(b_run,              2, 2)
        grid.setRowStretch (3, 1)

        self.setLayout(grid)
        self.setGeometry(200, 200, 400, 300)
  
        self.setToolTip("Train and run product recognition algorithms.")
        self.v_id.setToolTip("ID of current product.")
        
        b_train_curr.clicked.connect(self.train_current_recognizer)
        b_train_all.clicked.connect(self.train_all_recognizers)
        b_validate.clicked.connect(self.validate_recognizer)
        b_test.clicked.connect(self.test_recognizer)
        b_run.clicked.connect(self.run_recognizers)

  
    def setModel(self, model, recognizers, data):
        """Tell the widget which model it should use."""
        #Put model into communication object
        self.mapper.setModel(model)
        #Tell: which widget should show which column
        self.mapper.addMapping(self.v_id, 0, "text")
        #Go to first row
        self.mapper.toFirst()
        #set product recognizers and data storage.
        self.recognizers = recognizers
        self.data = data


    def setRow(self, index):
        """
        Set the row of the model that is accessed by the widget.
        
        Usually connected to signal ``activated`` of a ``QTreeView``.
        
        Parameter
        ---------
        index : QModelIndex
        """
        self.mapper.setCurrentModelIndex(index)

    def train_current_recognizer(self):
        "Train recognizer for current product"
        logging.debug("Train recognizer for current product")
        #Create progress dialog
        max_progress = 10
        progd = QProgressDialog("Train recognizer for current product", "Abort", 
                                0, max_progress, self)
        progd.setWindowModality(Qt.WindowModal)
        progd.setMinimumDuration(0)
        #Progress dialog only appears after a few calls to ``setValue``.
        for i in range(6): progd.setValue(i); time.sleep(0.01)
        #Get the current product
        curr_prod = self.v_id.text()
        prod_list = []
        for prod in self.data.products:
            if prod.id == curr_prod:
                prod_list.append(prod)
                break
        #Train the recognizer for this product
        self.recognizers.train_recognizers(prod_list, self.data.listings, progd)
        #Hide progress dialog
        progd.setValue(max_progress)
            
        
    def train_all_recognizers(self):
        "Train recognizers for all products."
        logging.debug("Train recognizers for all products.")
        #Create progress dialog
        max_progress = len(self.data.products) * 10
        progd = QProgressDialog("Train recognizers for all products", "Abort", 
                                0, max_progress, self)
        progd.setWindowModality(Qt.WindowModal)
        progd.setMinimumDuration(0)
        #Progress dialog only appears after a few calls to ``setValue``.
        for i in range(6): progd.setValue(i); time.sleep(0.01)
        #Train the recognizers
        self.recognizers.train_recognizers(self.data.products, 
                                           self.data.listings, progd)
        #Hide progress dialog
        progd.setValue(max_progress)
        
    def validate_recognizer(self):
        """
        Let recognizer recognize its own example data.
        
        Shows wrongly labeled samples, and recognition tasks that are 
        impossible for the recognizer.
        """
        print("Validate Recognizer")
    
    def test_recognizer(self):
        """
        Run recognizer over the last 500 listings where the current product is 
        expected.
        """ 
        print("Test Recognizer")
        
    def run_recognizers(self):
        """Run the recognizers over all listings."""
        logging.debug("Run Recognizers")
        #Create progress dialog
        max_progress = len(self.data.listings.index)
        progd = QProgressDialog("Recognize products in all listings.", "Abort", 
                                0, max_progress, self)
        progd.setWindowModality(Qt.WindowModal)
        progd.setMinimumDuration(0)
        #Run the recognizers
        self.recognizers.recognize_products(self.data.listings.index, 
                                            self.data.listings, progd)
        #Hide progress dialog
        progd.setValue(max_progress)
        #Record changes to listings and update GUI
        self.data.listings_dirty = True
        #TODO connect signal to suitable slot in listings model
        self.signalListingsChanged.emit()
        
    #The listings in the data store changed
    signalListingsChanged = pyqtSignal()



class ProductEditWidget(QWidget):
    """
    Display and edit contents of a single ``Product``.
    
    The data is taken from a row of a ``ProductModel``. 
    The communication between the model and the individual edit widgets, 
    is done by a ``QDataWidgetMapper``.  
    
    TODO: Important words and categories should be less high
    """
    def __init__(self):
        super(ProductEditWidget, self).__init__()
        
        #Transfers data between model and widgets
        self.mapper = QDataWidgetMapper()
        
        self.v_id = QLineEdit()
        self.e_name = QLineEdit()
        self.e_description = QTextEdit()
        self.e_important_words = QTextEdit()
        self.e_categories = QTextEdit()
        
        l_id = QLabel("ID")
        l_name = QLabel("Name")
        l_description = QLabel("Description")
        l_important_words = QLabel("Important Words")
        l_categories = QLabel("Categories")
        
        grid = QGridLayout()
        grid.addWidget(l_id,               0, 0)
        grid.addWidget(self.v_id,          0, 1, 1, 3)
        grid.addWidget(l_name,             1, 0)
        grid.addWidget(self.e_name,        1, 1, 1, 3)
        grid.addWidget(l_categories,       2, 0, 1, 2)
        grid.addWidget(self.e_categories,  3, 0, 2, 2)
        grid.addWidget(l_important_words,  2, 2, 1, 2)
        grid.addWidget(self.e_important_words,3, 2, 2, 2)
        grid.addWidget(l_description,      5, 0, 1, 4)
        grid.addWidget(self.e_description, 6, 0, 2, 4)
        grid.setRowStretch (6, 1)

        self.setLayout(grid)
        self.setGeometry(200, 200, 400, 300)
  
        self.setToolTip('Change information about a product.')
        self.v_id.setToolTip(Product.tool_tips["id"])
        self.e_name.setToolTip(Product.tool_tips["name"])
        self.e_important_words.setToolTip(Product.tool_tips["important_words"])
        self.e_categories.setToolTip(Product.tool_tips["categories"])
        self.e_description.setToolTip(Product.tool_tips["description"])

  
    def setModel(self, model):
        """Tell the widget which model it should use."""
        #Put model into communication object
        self.mapper.setModel(model)
        #Tell: which widget should show which column
        self.mapper.addMapping(self.v_id, 0)
        self.mapper.addMapping(self.e_name, 1)
        self.mapper.addMapping(self.e_categories, 2, "plainText")
        self.mapper.addMapping(self.e_important_words, 3, "plainText")
        self.mapper.addMapping(self.e_description, 4, "plainText")
        #Go to first row
        self.mapper.toFirst()


    def setRow(self, index):
        """
        Set the row of the model that is accessed by the widget.
        
        Usually connected to signal ``activated`` of a ``QTreeView``.
        
        Parameter
        ---------
        index : QModelIndex
        """
        self.mapper.setCurrentModelIndex(index)



class ProductWidget(QSplitter):
    """
    Display and edit a list of ``Product`` objects. There is a pane that shows
    the whole list, and an other pane that shows a single product.
    
    The data is taken from a ``ProductModel``.
    """
    def __init__(self, parent=None):
        super(ProductWidget, self).__init__(parent)
        self.edit_widget = ProductEditWidget()
        self.list_widget = QTreeView()
        self.reco_widget = RecognizerWidget()
        self.filter = QSortFilterProxyModel()
        self.sub_splitter = QSplitter()
        self.sub_splitter.setOrientation(Qt.Vertical)
        
        #Assemble the child widgets
        self.addWidget(self.list_widget)
        self.addWidget(self.sub_splitter)
        self.sub_splitter.addWidget(self.edit_widget)
        self.sub_splitter.addWidget(self.reco_widget)
    
        #Set various options of the view. #TODO: Delete unnecessary
        self.list_widget.setItemsExpandable(False)
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget.setDragEnabled(False)
        self.list_widget.setAcceptDrops(False)
        self.list_widget.setDropIndicatorShown(True)
        self.list_widget.setDefaultDropAction(Qt.MoveAction)
#        self.list_widget.setEditTriggers(QAbstractItemView.EditKeyPressed |
#                                         #QAbstractItemView.AnyKeyPressed |
#                                         QAbstractItemView.SelectedClicked)
        self.list_widget.setRootIsDecorated(False)
        self.list_widget.setSortingEnabled(True)
        self.list_widget.setContextMenuPolicy(Qt.ActionsContextMenu)
        
        #Create context menu for list view
        self.action_new = QAction("&New Product", self)
        self.action_new.setShortcuts(QKeySequence.InsertLineSeparator)
        self.action_new.setStatusTip(
                                "Create new product below selected product.")
        self.action_new.triggered.connect(self.newProduct)
        self.list_widget.addAction(self.action_new)
        self.action_delete = QAction("&Delete Product", self)
        self.action_delete.setShortcuts(QKeySequence.Delete)
        self.action_delete.setStatusTip("Delete selected product.")
        self.action_delete.triggered.connect(self.deleteProduct)
        self.list_widget.addAction(self.action_delete)
        
        self.filter.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.filter.setDynamicSortFilter(False)
        

    def setModel(self, product_model, recognizers, data):
        """Tell view which model it should display and edit."""
        self.filter.setSourceModel(product_model)
        self.edit_widget.setModel(self.filter)
        self.reco_widget.setModel(self.filter, recognizers, data)
        self.list_widget.setModel(self.filter)
        #When user selects a line in ``list_widget`` this item is shown 
        #in ``edit_widget``
        self.list_widget.selectionModel().currentRowChanged.connect(
                                                        self.slotRowChanged)
    
    def slotRowChanged(self, current, _previous):
        """
        The selected row has changed. Tells edit widget to show this row.
        Connected to signal ``currentRowChanged`` of 
        ``list_widget.selectionModel()``
        """
        self.edit_widget.setRow(current)
        self.reco_widget.setRow(current)
        
    def newProduct(self):
        """Create a new product below the current product."""
        row = self.list_widget.currentIndex().row()
        model = self.list_widget.model()
        model.insertRows(row + 1, 1)
        index = model.index(row + 1, 0, QModelIndex())
        self.edit_widget.setRow(index)
        self.list_widget.setCurrentIndex(index)
        
    def deleteProduct(self):
        """Delete the current product."""
        row = self.list_widget.currentIndex().row()
        model = self.list_widget.model()
        model.removeRows(row, 1)
        
    def saveSettings(self, setting_store):
        """Save widget state, such as splitter position."""
        setting_store.setValue("ProductWidget/state", self.saveState())
        setting_store.setValue("ProductWidget/list/header/state", 
                               self.list_widget.header().saveState())
        setting_store.setValue("ProductWidget/sub_splitter/state", 
                               self.sub_splitter.saveState())
        
    def loadSettings(self, setting_store):
        """Load widget state, such as splitter position."""
        self.restoreState(setting_store.value("ProductWidget/state", ""))
        self.list_widget.header().restoreState(
                setting_store.value("ProductWidget/list/header/state", ""))
        self.sub_splitter.restoreState(
                setting_store.value("ProductWidget/sub_splitter/state", ""))



class ProductModel(QAbstractTableModel):
    """
    Represent a list of ``Product`` objects to QT's model view architecture.
    An adapter in design pattern language.
    """
    def __init__(self, parent=None):
        super(ProductModel, self).__init__(parent)
        self.data_store = DataStore() #Dummy
    
    def setDataStore(self, data_store):
        """Put list of products into model"""
        #Tell the view(s) that old data is gone.
        self.beginRemoveRows(QModelIndex(), 0, len(self.data_store.products))
        self.endRemoveRows()
        #Change the data
        self.data_store = data_store
        #Tell the view(s) that all data has changed.
        self.layoutChanged.emit()

    def slotDataChanged(self):
        "Signal the model that the underlying data has changed."
        self.beginResetModel()
        self.endResetModel()
        
    def rowCount(self, parent=QModelIndex()):
        """Return number of products in list."""
        if parent.isValid(): #There are only top level items
            return 0
        return len(self.data_store.products)
    
    def columnCount(self, parent=QModelIndex()):
        """Return number of accessible product attributes."""
        if parent.isValid(): #There are only top level items
            return 0
        return 5
    
    def supportedDropActions(self):
        """Say which actions are supported for drag-drop."""
        return Qt.CopyAction | Qt.MoveAction
 
    def flags(self, index):
        """
        Determines the possible actions for the item at this index.
        
        Parameters
        ----------
        index: QModelIndex
        """
        default_flags = super(ProductModel, self).flags(index)
        
        if index.isValid():
            return Qt.ItemIsDragEnabled | Qt.ItemIsEditable | default_flags
        else:
            return Qt.ItemIsDropEnabled | default_flags
    
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Return the text for the column headers.
        
        Parameters
        -----------
        section: int
            Column number
        orientation: 
            Qt.Vertical or Qt.Horizontal
        role: int
        """
        if orientation != Qt.Horizontal or role != Qt.DisplayRole:
            return None
        header_names = ["ID", "Name", "Categories", "Important Words", 
                        "Description"]
        return header_names[section]


    attr_names = ["id", "name", "categories", "important_words", "description"]
    
    def data(self, index, role=Qt.DisplayRole):
        """
        Return the contents of the product list in the right way.
        
        Parameters
        -----------
        index: QModelIndex
        role: int 
        """
#        assert index.model() == self
        if not index.isValid():
            return None
        
        row = index.row()
        column = index.column()
        attr_name = ProductModel.attr_names[column]
        
        if role  == Qt.DisplayRole:
            #Return only one line of big fields for list view
            prod = self.data_store.products[row]
            if attr_name in ["categories", "important_words"]:
                attr = getattr(prod, attr_name)
                return attr[0] if attr else ""
            elif attr_name == "description":
                description = prod.description
                return description.split("\n")[0]
            else:
                return getattr(prod, attr_name)
        elif role == Qt.EditRole:
            #Return full data for editing
            prod = self.data_store.products[row]
            if attr_name in ["categories", "important_words"]:
                attr = getattr(prod, attr_name)
                return u"\n".join(attr)
            else:
                return getattr(prod, attr_name)
        elif role == Qt.ToolTipRole:
            return Product.tool_tips[attr_name]
                        
        return None
    
    
    def setData(self, index, value, role=Qt.EditRole):
        """
        Change the data in the model.
        
        Parameters
        ----------
        index : QModelIndex
        value: object
        role : int
        
        Retuns
        ------
        bool
            Returns ``True`` if data was changed successfully, 
            returns ``False`` otherwise.
        
        TODO: Warning when ID is changed
        """
        assert index.model() == self
        if role != Qt.EditRole:
            return False
        if not index.isValid():
            return False
        
        row = index.row()
        column = index.column()
        attr_name = ProductModel.attr_names[column]
        prod = self.data_store.products[row]
        
        if attr_name in ["categories", "important_words"]:
            val_list = value.split("\n")
            setattr(prod, attr_name, val_list)
        else:
            setattr(prod, attr_name, value)
            
        self.data_store.products_dirty = True
        self.dataChanged.emit(index, index)
        return True
    
    
    def setItemData(self, index, roles):
        """
        Change data in model. Intention is to change data more efficiently,
        because data with with several roles is changed at once.
        
        Parameters
        ----------
        index : QModelIndex
        roles : dict[int, object]
        
        Retuns
        ------
        bool
            Returns ``True`` if data was changed successfully, 
            returns ``False`` otherwise.
        """
        #Only data with Qt.EditRole can be changed
        if Qt.EditRole not in roles:
            return False
        return self.setData(index, roles[Qt.EditRole], Qt.EditRole)
    
        
    def insertRows(self, row, count, parent=QModelIndex()):
        """
        Insert "empty" products into the list of products.
        
        Parameters
        ----------
        row : int
            The new rows are inserted before the row with this index
        count : int
            Number of rows that are inserted.
        parent : QModelIndex
        
        Returns
        -------
        bool
            Returns True if rows were inserted successfully, False otherwise.
        """
        if parent.isValid(): #There are only top level items
            return False
        
        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            new_prod = Product(u"---", u"", u"", [], [])
            self.data_store.products.insert(row + i, new_prod)
        self.endInsertRows()
        
        self.data_store.products_dirty = True
        return True
    
    
    def removeRows(self, row, count, parent=QModelIndex()):
        """
        Remove products from the list.
        
        Parameters
        ----------
        row : int
            Index of first row that is removed.
        count : int
            Number of rows that are removed.
        parent : QModelIndex
        
        Returns
        -------
        bool
            Returns True if rows were removed successfully, False otherwise.

        """
        if parent.isValid(): #There are only top level items
            return False
        
        self.beginRemoveRows(parent, row, row + count - 1)
        del self.data_store.products[row:row + count]
        self.endRemoveRows()
        
        self.data_store.products_dirty = True
        return True


    def getProductByID(self, prod_id):
        """
        Access products though their product ID. 
        Do not change products through this method!
        Returns: Product | None
        """
        for prod in self.data_store.products:
            if prod.id == prod_id:
                return prod
        else:
            return None
    
    def getProductIDList(self):
        """Return IDs of all products stored in the model."""
        prod_ids = [p.id for p in self.data_store.products]
        prod_ids.sort()
        return prod_ids
        
        

class SearchTaskEditWidget(QWidget):
    """
    Display and edit contents of a single ``SearchTask``.
    
    The data is taken from a row of a ``TaskModel``. 
    The communication between the model and the individual edit widgets, 
    is done by a ``QDataWidgetMapper``.
    """
    def __init__(self):
        super(SearchTaskEditWidget, self).__init__()
        
        #Transfers data between model and widgets
        self.mapper = QDataWidgetMapper()
        
        #The task's contents
        self.e_id = QLineEdit()
        self.e_due_time = QLineEdit()
        self.e_server = QLineEdit()
        self.e_recurrence_pattern = QLineEdit()
        self.e_query_string = QLineEdit()
        self.e_n_listings = QLineEdit()
        self.e_price_min = QLineEdit()
        self.e_price_max = QLineEdit()
        self.e_currency = QLineEdit()
        self.e_expected_products = QTextEdit()
        l_id = QLabel("ID")
        l_due_time = QLabel("Due Time")
        l_server = QLabel("Server")
        l_recurrence_pattern = QLabel("Recurrence")
        l_query_string = QLabel("Query String")
        l_n_listings = QLabel("Number Listings")
        l_price_min = QLabel("Price Min")
        l_price_max = QLabel("Price Max")
        l_currency2 = QLineEdit("---") #Use disabled QLineEdit as label 
        l_currency2.setEnabled(False)
        l_expected_products = QLabel("Expected Products")
        #Let e_currency and l_currency2 contain the same text
        self.e_currency.textChanged.connect(l_currency2.setText)
        
        grid = QGridLayout()
        grid.addWidget(l_id, 0, 0)
        grid.addWidget(self.e_id, 0, 1, 1, 2)
        grid.addWidget(l_due_time, 1, 0)
        grid.addWidget(self.e_due_time, 1, 1, 1, 2)
        grid.addWidget(l_server, 2, 0)
        grid.addWidget(self.e_server, 2, 1, 1, 2)
        grid.addWidget(l_recurrence_pattern, 3, 0)
        grid.addWidget(self.e_recurrence_pattern, 3, 1, 1, 2)
        grid.addWidget(l_query_string, 4, 0)
        grid.addWidget(self.e_query_string, 4, 1, 1, 2)
        grid.addWidget(l_n_listings, 5, 0)
        grid.addWidget(self.e_n_listings, 5, 1, 1, 2)
        grid.addWidget(l_price_min, 6, 0)
        grid.addWidget(self.e_price_min, 6, 1, 1, 1)
        grid.addWidget(l_price_max, 7, 0)
        grid.addWidget(self.e_price_max, 7, 1, 1, 1)
        grid.addWidget(self.e_currency, 6, 2)
        grid.addWidget(l_currency2, 7, 2)
        grid.addWidget(l_expected_products, 8, 0, 1, 3)
        grid.addWidget(self.e_expected_products, 9, 0, 2, 3)
        grid.setRowStretch (10, 1)
        
        self.setLayout(grid)
        self.setGeometry(200, 200, 400, 300)
  
        self.setToolTip('Change information about a search task.')
        self.e_id.setToolTip(SearchTask.tool_tips["id"])
        self.e_due_time.setToolTip(SearchTask.tool_tips["due_time"])
        self.e_server.setToolTip(SearchTask.tool_tips["server"])
        self.e_recurrence_pattern.setToolTip(
                                    SearchTask.tool_tips["recurrence_pattern"])
        self.e_query_string.setToolTip(SearchTask.tool_tips["query_string"])
        self.e_n_listings.setToolTip(SearchTask.tool_tips["n_listings"])
        self.e_price_min.setToolTip(SearchTask.tool_tips["price_min"])
        self.e_price_max.setToolTip(SearchTask.tool_tips["price_max"])
        self.e_currency.setToolTip(SearchTask.tool_tips["currency"])
        self.e_expected_products.setToolTip(
                                    SearchTask.tool_tips["expected_products"])
  
    def setModel(self, model):
        """Tell the widget which model it should use."""
        #Put model into communication object
        self.mapper.setModel(model)
        #Tell: which widget should show which column
        self.mapper.addMapping(self.e_id, 0)
        self.mapper.addMapping(self.e_due_time, 1)
        self.mapper.addMapping(self.e_server, 2)
        self.mapper.addMapping(self.e_recurrence_pattern, 3)
        self.mapper.addMapping(self.e_query_string, 4)
        self.mapper.addMapping(self.e_n_listings, 5)
        self.mapper.addMapping(self.e_price_min, 6)
        self.mapper.addMapping(self.e_price_max, 7)
        self.mapper.addMapping(self.e_currency, 8)
        self.mapper.addMapping(self.e_expected_products, 9, "plainText")
        #Go to first row
        self.mapper.toFirst()


    def setRow(self, index):
        """
        Set the row of the model that is accessed by the widget.
        
        Usually connected to signal ``activated`` of a ``QTreeView``.
        
        Parameter
        ---------
        index : QModelIndex
        """
        self.mapper.setCurrentModelIndex(index)



class TaskWidget(QSplitter):
    """
    Display and edit a list of ``Product`` objects. There is a pane that shows
    the whole list, and an other pane that shows a single task.
    
    The data is taken from a ``ProductModel``.
    """
    def __init__(self, parent=None):
        super(TaskWidget, self).__init__(parent)
        self.edit_widget = SearchTaskEditWidget()
        self.list_widget = QTreeView()
        self.filter = QSortFilterProxyModel()
        self.data_store = DataStore() #Dummy
        
        #Assemble the child widgets
        self.addWidget(self.list_widget)
        self.addWidget(self.edit_widget)
    
        #Set various options of the view. #TODO: Delete unnecessary
        self.list_widget.setItemsExpandable(False)
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget.setDragEnabled(False)
        self.list_widget.setAcceptDrops(False)
        self.list_widget.setDropIndicatorShown(True)
        self.list_widget.setDefaultDropAction(Qt.MoveAction)
#        self.list_widget.setEditTriggers(QAbstractItemView.EditKeyPressed |
#                                         #QAbstractItemView.AnyKeyPressed |
#                                         QAbstractItemView.SelectedClicked)
        self.list_widget.setRootIsDecorated(False)
        self.list_widget.setSortingEnabled(True)
        self.list_widget.setContextMenuPolicy(Qt.ActionsContextMenu)
        
        #Create context menu for list view
        #New Task
        self.action_new = QAction("&New Task", self)
        self.action_new.setShortcuts(QKeySequence.InsertLineSeparator)
        self.action_new.setToolTip("Create new task below selected task.")
        self.action_new.triggered.connect(self.newProduct)
        self.list_widget.addAction(self.action_new)
        #Delete task
        self.action_delete = QAction("&Delete Task", self)
        self.action_delete.setShortcuts(QKeySequence.Delete)
        self.action_delete.setToolTip("Delete selected task.")
        self.action_delete.triggered.connect(self.deleteProduct)
        self.list_widget.addAction(self.action_delete)
        #Separator
        separator = QAction(self)
        separator.setSeparator(True)
        self.list_widget.addAction(separator)
        #Update expected products
        self.action_update_expected_products = \
            QAction("&Update Expected Products", self)
        self.action_update_expected_products.setToolTip(
            "Update 'expected products' field of current task, and of all "
            "listings that were fond by this task.")
        self.action_update_expected_products.triggered.connect(
            self.update_expected_products)
        self.list_widget.addAction(self.action_update_expected_products)
        #Set expected products to listings
        self.action_set_expected_products = \
            QAction("&Set Expected Products", self)
        self.action_set_expected_products.setToolTip(
            "Copy value of 'expected_products' from current task to all "
            "related listings.")
        self.action_set_expected_products.triggered.connect(
            self.set_expected_products)
        self.list_widget.addAction(self.action_set_expected_products)
        
        #Parameters for the sort filter
        self.filter.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.filter.setDynamicSortFilter(False)


    def setModel(self, task_model, listings_model, data_store):
        """Tell view which model it should display and edit."""
        self.filter.setSourceModel(task_model)
        self.edit_widget.setModel(self.filter)
        self.list_widget.setModel(self.filter)
        self.data_store = data_store
        #When user selects a line in ``list_widget`` this item is shown 
        #in ``edit_widget``
        self.list_widget.selectionModel().currentRowChanged.connect(
                                                        self.slotRowChanged)
        #Notify models when their underlying data has changed
        self.signalTasksChanged.connect(task_model.slotDataChanged)
        self.signalListingsChanged.connect(listings_model.slotDataChanged)
    
    def slotRowChanged(self, current, _previous):
        """
        The selected row has changed. Tells edit widget to show this row.
        Connected to signal ``currentRowChanged`` of 
        ``list_widget.selectionModel()``
        """
        self.edit_widget.setRow(current)
        
    def newProduct(self):
        """Create a new product below the current product."""
        row = self.list_widget.currentIndex().row()
        model = self.list_widget.model()
        model.insertRows(row + 1, 1)
        index = model.index(row + 1, 0, QModelIndex())
        self.edit_widget.setRow(index)
        self.list_widget.setCurrentIndex(index)
        
    def deleteProduct(self):
        """Delete the current product."""
        row = self.list_widget.currentIndex().row()
        model = self.list_widget.model()
        model.removeRows(row, 1)
    
    #The listings in the data store changed completely
    signalListingsChanged = pyqtSignal()
    #The tasks in the data store changed completely
    signalTasksChanged = pyqtSignal()
        
    def update_expected_products(self):
        """
        Scan example listings that were found by the current task_id_or_number 
        for contained products, and put them into the task_id_or_number's 
        'expected products' field. Then put the updated list of 
        'expected products' into the listings.
        """
        curr_idx = self.list_widget.currentIndex()
        task_id_idx = curr_idx.sibling(curr_idx.row(), 0)
        task_id = task_id_idx.data()
        self.data_store.update_expected_products(task_id)
        self.signalListingsChanged.emit()
        self.signalTasksChanged.emit()
        
    def set_expected_products(self):
        """
        Copy value of ``expected_products`` from the current task to all
        related listings. Related listings are listings that were fund by
        this task.
        """
        curr_idx = self.list_widget.currentIndex()
        task_id_idx = curr_idx.sibling(curr_idx.row(), 0)
        task_id = task_id_idx.data()
        self.data_store.write_expected_products_to_listings(task_id)
        self.signalListingsChanged.emit()
        self.signalTasksChanged.emit()        
        
    def saveSettings(self, setting_store):
        """Save widget state, such as splitter position."""
        setting_store.setValue("TaskWidget/state", self.saveState())
        setting_store.setValue("TaskWidget/list/header/state", 
                               self.list_widget.header().saveState())
        
    def loadSettings(self, setting_store):
        """Load widget state, such as splitter position."""
        self.restoreState(setting_store.value("TaskWidget/state", ""))
        self.list_widget.header().restoreState(
                setting_store.value("TaskWidget/list/header/state", ""))



class TaskModel(QAbstractTableModel):
    """
    Represent a list of tasks (currently only ``SearchTask``) to QT's model 
    view architecture.
    An adapter in design pattern language.
    """
    def __init__(self, parent=None):
        super(TaskModel, self).__init__(parent)
        self.data_store = DataStore() #Dummy
    
    def setDataStore(self, data_store):
        """Put list of tasks into model"""
        #Tell the view(s) that old data is gone.
        self.beginRemoveRows(QModelIndex(), 0, len(self.data_store.tasks))
        self.endRemoveRows()
        #Change the data
        self.data_store = data_store
        #Tell the view(s) that all data has changed.
        self.layoutChanged.emit()

    def slotDataChanged(self):
        "Signal the model that the underlying data has changed."
        self.beginResetModel()
        self.endResetModel()
        
    def rowCount(self, parent=QModelIndex()):
        """Return number of tasks in list."""
        if parent.isValid(): #There are only top level items
            return 0
        return len(self.data_store.tasks)
    
    def columnCount(self, parent=QModelIndex()):
        """Return number of accessible task attributes."""
        if parent.isValid(): #There are only top level items
            return 0
        return 10
    
    def supportedDropActions(self):
        """Say which actions are supported for drag-drop."""
        return Qt.CopyAction | Qt.MoveAction
 
    def flags(self, index):
        """
        Determines the possible actions for the item at this index.
        
        Parameters
        ----------
        index: QModelIndex
        """
        default_flags = super(TaskModel, self).flags(index)
        
        if index.isValid():
            return Qt.ItemIsDragEnabled | Qt.ItemIsEditable | default_flags
        else:
            return Qt.ItemIsDropEnabled | default_flags
    
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Return the text for the column headers.
        
        Parameters
        -----------
        section: int
            Column number
        orientation: 
            Qt.Vertical or Qt.Horizontal
        role: int
        """
        if orientation != Qt.Horizontal or role != Qt.DisplayRole:
            return None
        header_names = ["ID", "Due Time", "Server", "Recurrence Pattern", 
                        "Query String", "Number Listings", "Price Min", 
                        "Price Max", "Currency", "Expected Products"]
        return header_names[section]


    attr_names = ["id", "due_time", "server", "recurrence_pattern", 
                  "query_string", "n_listings", "price_min", "price_max", 
                  "currency", "expected_products"]

    def data(self, index, role=Qt.DisplayRole):
        """
        Return the contents of the task list in the right way.
        
        Parameters
        -----------
        index: QModelIndex
        role: int 
        """
#        assert index.model() == self
        if not index.isValid():
            return None
        
        row = index.row()
        column = index.column()
        attr_name = TaskModel.attr_names[column]
        
        if role == Qt.DisplayRole:
            #Return only one line of big fields for list view
            task = self.data_store.tasks[row]
            if attr_name == "due_time":
                return to_text_time(task.due_time)
            elif attr_name == "expected_products":
                expected_products = task.expected_products
                return expected_products[0] if expected_products else ""
            else:
                return getattr(task, attr_name)
        elif role == Qt.EditRole:
            #Return full data for editing
            task = self.data_store.tasks[row]
            if attr_name == "due_time":
                return to_text_time(task.due_time)
            elif attr_name == "expected_products":
                return u"\n".join(task.expected_products)
            else:
                return getattr(task, attr_name)
        elif role == Qt.ToolTipRole:
            return SearchTask.tool_tips[attr_name]
                        
        return None
    
    
    def setData(self, index, value, role=Qt.EditRole):
        """
        Change the data in the model.
        
        Parameters
        ----------
        index : QModelIndex
        value: object
        role : int
        
        Retuns
        ------
        bool
            Returns ``True`` if data was changed successfully, 
            returns ``False`` otherwise.
        
        TODO: Warning when ID is changed
        """
        assert index.model() == self
        if role != Qt.EditRole:
            return False
        if not index.isValid():
            return False
        
        row = index.row()
        column = index.column()
        task = self.data_store.tasks[row]
        attr_name = TaskModel.attr_names[column]
        
        if attr_name == "due_time":
            try:
                task.due_time = dateutil.parser.parse(value)
            except ValueError:
                return False
        elif attr_name == "expected_products":
            task.expected_products = value.split(u"\n")
        else:
            setattr(task, attr_name, value)
        
        self.data_store.tasks_dirty = True
        self.dataChanged.emit(index, index)
        return True
    
    
    def setItemData(self, index, roles):
        """
        Change data in model. Intention is to change data more efficiently,
        because data with with several roles is changed at once.
        
        Parameters
        ----------
        index : QModelIndex
        roles : dict[int, object]
        
        Retuns
        ------
        bool
            Returns ``True`` if data was changed successfully, 
            returns ``False`` otherwise.
        """
        #Only data with Qt.EditRole can be changed
        if Qt.EditRole not in roles:
            return False
        return self.setData(index, roles[Qt.EditRole], Qt.EditRole)
    
        
    def insertRows(self, row, count, parent=QModelIndex()):
        """
        Insert "empty" tasks into the list of tasks.
        
        Parameters
        ----------
        row : int
            The new rows are inserted before the row with this index
        count : int
            Number of rows that are inserted.
        parent : QModelIndex
        
        Returns
        -------
        bool
            Returns True if rows were inserted successfully, False otherwise.
        """
        if parent.isValid(): #There are only top level items
            return False
        
        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            new_prod = SearchTask("--", datetime(9999, 12, 31), "", "", 
                                  "daily", 100, 0, 1000, "EUR", [])
            self.data_store.tasks.insert(row + i, new_prod)
        self.endInsertRows()
        
        self.data_store.tasks_dirty = True
        return True
    
    
    def removeRows(self, row, count, parent=QModelIndex()):
        """
        Remove tasks from the list.
        
        Parameters
        ----------
        row : int
            Index of first row that is removed.
        count : int
            Number of rows that are removed.
        parent : QModelIndex
        
        Returns
        -------
        bool
            Returns True if rows were removed successfully, False otherwise.

        """
        if parent.isValid(): #There are only top level items
            return False
        
        self.beginRemoveRows(parent, row, row + count - 1)
        del self.data_store.tasks[row:row + count]
        self.endRemoveRows()
        
        self.data_store.tasks_dirty = True
        return True



class RadioButtonModel(QAbstractTableModel):
    """
    Represent a matrix of binary values, together with text fields. 
    However each row acts like a group of radio buttons: 
    Only one value in each row can be True, all others must be False.
    """
    def __init__(self, n_binvals, n_textvals, editable_cols, parent=None):
        assert isinstance(n_binvals, int)
        assert isinstance(n_textvals, int)
        assert isinstance(editable_cols, list)
        assert all([isinstance(i, int) for i in editable_cols])
        super(RadioButtonModel, self).__init__(parent)
        #number of bool values at start of row
        self.n_binvals = n_binvals
        #Number of other (text) values at end of row
        self.n_textvals = n_textvals
        #The column indexes of columns that can be edited: list[int]
        self.editable_cols = editable_cols
        #The stored values, nested list, first index rows, second columns: 
        #list[list[int, int, ..., str, str, ...]]
        #Boolean values for check boxes are really tri-state: 
        #0: unchecked, 1: partially checked, 2: checked 
        self.values = []
        self.header_names = ["" for _ in range(self.n_binvals + 
                                               self.n_textvals)]
        self.tool_tips = ["" for _ in range(self.n_binvals + self.n_textvals)]
        #True if values were changed
        self.dirty = False
    
    def changeUnderlyingData(self):
        """
        Change the data from which ``self.values`` is constructed.
        Should be re-implemented in derived class, or monkey-patched.
        """
        pass
    
    def setValues(self, values):
        """
        Change all elements of the table at once.
        
        Argument
        --------
        values : list[list[bool, bool, ..., str, str, ...]]
            Nested list, first index rows, second index columns.
            First columns are binary values (number: ``self.n_binvals``),
            remaining columns are strings (number: ``self.n_textvals``).  
        """
        assert isinstance(values, list) 
        for row in values:
            assert isinstance(row, list)
            assert len(row) == self.n_binvals + self.n_textvals
            
        #Tell the view(s) that old data is gone.
        self.beginRemoveRows(QModelIndex(), 0, len(self.values))
        self.endRemoveRows()
        #Change the data
        self.values = values
        self.dirty = False
        #Tell the view(s) that all data has changed.
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()):
        """Return number of rows."""
        if parent.isValid(): #There are only top level items
            return 0
        return len(self.values)
    
    def columnCount(self, parent=QModelIndex()):
        """Return number of columns."""
        if parent.isValid(): #There are only top level items
            return 0
        return self.n_binvals + self.n_textvals
    
    def supportedDropActions(self):
        """Say which actions are supported for drag-drop."""
        return Qt.MoveAction
 
    def flags(self, index):
        """
        Determines the possible actions for the item at this index.
        
        Parameters
        ----------
        index: QModelIndex
        """
        flags = super(RadioButtonModel, self).flags(index)
                    
        if index.isValid():
            icol = index.column()
            if icol in self.editable_cols:
                flags |= Qt.ItemIsEditable
            if icol < self.n_binvals:
                flags |= Qt.ItemIsUserCheckable
        
        return flags
    
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Return the text for the column headers.
        
        Parameters
        -----------
        section: int
            Column number
        orientation: 
            Qt.Vertical or Qt.Horizontal
        role: int
        """
        if orientation != Qt.Horizontal or role != Qt.DisplayRole:
            return None
        
        return self.header_names[section]


    def data(self, index, role=Qt.DisplayRole):
        """
        Return the contents of the array at a certain index.
        
        Parameters
        -----------
        index: QModelIndex
        role: int 
        """
#        assert index.model() == self
        if not index.isValid():
            return None

        irow = index.row()
        icol = index.column()
        
        if icol < self.n_binvals and role in [Qt.CheckStateRole]:
            return self.values[irow][icol]
        elif icol >= self.n_binvals and role in [Qt.DisplayRole, Qt.EditRole]:
            return self.values[irow][icol]
        elif role == Qt.ToolTipRole:
            return self.tool_tips[icol]
                        
        return None
    
    
    def setData(self, index, value, role=Qt.EditRole):
        """
        Change the data in the model.
        
        Parameters
        ----------
        index : QModelIndex
        value: object
        role : int
        
        Retuns
        ------
        bool
            Returns ``True`` if data was changed successfully, 
            returns ``False`` otherwise.
        """
#        assert index.model() == self
        if role not in [Qt.EditRole, Qt.CheckStateRole]:
            return False
        if not index.isValid():
            return False
        
        irow = index.row()
        icol = index.column()
        row = self.values[irow]
        if icol < self.n_binvals:
            #The binary values act like radio buttons: only one can be True
            row[0:self.n_binvals] = [0] * self.n_binvals
            row[icol] = value #Tree view sets ``2`` for checked
        else:
            #The other fields act as regular fields
            row[icol] = value
            
        self.dirty = True
        self.dataChanged.emit(self.index(irow, 0), 
                              self.index(irow, self.n_binvals - 1))
        self.changeUnderlyingData()
        return True
    
    
    def setItemData(self, index, roles):
        """
        Change data in model. Intention is to change data more efficiently,
        because data with with several roles is changed at once.
        
        Parameters
        ----------
        index : QModelIndex
        roles : dict[int, object]
        
        Retuns
        ------
        bool
            Returns ``True`` if data was changed successfully, 
            returns ``False`` otherwise.
        """
        #Only data with Qt.EditRole or Qt.CheckState can be changed
        if Qt.CheckState in roles:
            return self.setData(index, roles[Qt.CheckState], Qt.CheckState)
        elif Qt.EditRole in roles:
            return self.setData(index, roles[Qt.EditRole], Qt.EditRole)
        else:
            return False
    
        
    def insertRows(self, row, count, parent=QModelIndex()):
        """
        Insert "empty" rows into the list.
        
        Parameters
        ----------
        row : int
            The new rows are inserted before the row with this index
        count : int
            Number of rows that are inserted.
        parent : QModelIndex
        
        Returns
        -------
        bool
            Returns True if rows were inserted successfully, False otherwise.
        """
        if parent.isValid(): #There are only top level items
            return False
        
        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            new_row = [False for _ in range(self.n_binvals)] + \
                      [""    for _ in range(self.n_textvals)]
            self.values.insert(row + i, new_row)
        self.endInsertRows()
        
        self.dirty = True
        self.changeUnderlyingData()
        return True
    
    
    def removeRows(self, row, count, parent=QModelIndex()):
        """
        Remove rows from the list.
        
        Parameters
        ----------
        row : int
            Index of first row that is removed.
        count : int
            Number of rows that are removed.
        parent : QModelIndex
        
        Returns
        -------
        bool
            Returns True if rows were removed successfully, False otherwise.

        """
        if parent.isValid(): #There are only top level items
            return False
        
        self.beginRemoveRows(parent, row, row + count - 1)
        del self.values[row:row + count]
        self.endRemoveRows()
        
        self.dirty = True
        self.changeUnderlyingData()
        return True



class LearnDataProxyModel(RadioButtonModel):
    """
    Convert data for learning and product recognition to format suitable for
    display in GUI. Operates on one row of a ``ListingsModel``.
    """
    def __init__(self, parent=None):
        super(LearnDataProxyModel, self).__init__(2, 2, [2], parent)
        #The learning data is taken from this model
        self.source_model = ListingsModel() #dummy
        #Model from which the product names are taken.
        self.product_model = ProductModel() #dummy
        #Index that points to current row
        self.row_index = self.source_model.index(0, 0)
        #Columns from where source data is taken
        self.col_expected_products = None
        self.col_products = None
        self.col_products_absent = None
        #Contents of column headers
        self.header_names = ["Present", "Absent", "ID", "Name"]
        self.tool_tips = ["Product is present in this listing.",
                          "Product is absent in this listing.",
                          "Product ID",
                          "Product name"]
        
    def setSourceModel(self, model, 
                       expected_products, products, products_absent):
        """Change model and columns from which the learning data is taken."""
        assert isinstance(model, QAbstractItemModel)
        assert isinstance(expected_products, int)
        assert isinstance(products, int)
        assert isinstance(products_absent, int)
        self.source_model = model
        self.col_expected_products = expected_products
        self.col_products = products
        self.col_products_absent = products_absent    
        
    def setProductModel(self, product_model):
        """Set model from which the product names are taken."""
        assert hasattr(product_model, "getProductByID")
        self.product_model = product_model
        
    def setRow(self, index):
        """Set the row of source model that is accessed."""
        assert isinstance(index, QModelIndex)
        self.row_index = index
        self.changeGuiData()

    def changeGuiData(self):
        """Compute the GUI data, and change it."""
        #Get the data from the source model
        irow = self.row_index.row()
        sm = self.source_model
        expected_products = sm.data(sm.index(irow, self.col_expected_products), 
                                    Qt.EditRole)
        products          = sm.data(sm.index(irow, self.col_products), 
                                    Qt.EditRole)
        products_absent   = sm.data(sm.index(irow, self.col_products_absent), 
                                    Qt.EditRole)
        #Convert None to empty list
        none2list = lambda l: l if l is not None else []
        expected_products = none2list(expected_products)
        products = none2list(products)
        products_absent = none2list(products_absent)
        
        #create list of all used product IDs
        #preserve sequence of expected_products, additional ID are appended
        #TODO: remove duplicates from _expected_products
        mentioned_prods = set(products + products_absent)
        expected_missing = mentioned_prods - set(expected_products)
        product_id_list = expected_products + list(expected_missing)
        
        gui_vals = []
        for prod_id in product_id_list:
            product = self.product_model.getProductByID(prod_id)
            prod_name = product.name if product is not None else ""
            row = [0, 0, prod_id, prod_name]
            if prod_id in products:
                row[0] = 2 #checkboxes are tristate: 2 == fully checked
            if prod_id in products_absent:
                row[1] = 2
            gui_vals.append(row)
            
        #Add one empty row as means to add products to list
        gui_vals.append([0, 0, "", ""])
        self.setValues(gui_vals)
        
        
    def changeUnderlyingData(self):
        """Compute data for learning algorithm from GUI data."""
        #TODO: update field ``expected_products`` of related search tasks
        expected_products = []
        products = []
        products_absent = []
        for row in self.values:
            prod = unicode(row[2]).strip()
            #rows with no product IDs are considered deleted
            if  prod == u"":
                continue
            expected_products.append(prod)
            if row[0] and row[1]:
                pass
            elif row[0]:
                products.append(prod)
            elif row[1]:
                products_absent.append(prod)
        
        #Put data into source model
        irow = self.row_index.row()
        sm = self.source_model
        sm.setData(sm.index(irow, self.col_expected_products), 
                   expected_products, Qt.EditRole)
        sm.setData(sm.index(irow, self.col_products), products,Qt.EditRole)
        sm.setData(sm.index(irow, self.col_products_absent), 
                   products_absent, Qt.EditRole)
        
        #Update visible information, mainly for column 3, product name
        self.changeGuiData()
#        #Add one empty row as means to add products to list, if necessary
#        if self.values[-1][2] != "":
#            self.changeGuiData()



class WritableCurrentTextComboBox(QComboBox):
    """
    Special ``QComboBox`` with writable property ``currentText``, that contains 
    the current text. Used by ``EditorCreatorComboBox``.
    """
    def __init__(self, parent):
        super(WritableCurrentTextComboBox, self).__init__(parent)
        
    def getCurrentText(self):
        return super(WritableCurrentTextComboBox, self).currentText()
    def setCurrentText(self, text):
        self.setEditText(text)
    currentText = pyqtProperty(unicode, user=True,
                               fget=getCurrentText, fset=setCurrentText, 
                               doc="Text that is currently in line edit.")
    
    
    
class EditorCreatorComboBox(QItemEditorCreatorBase):
    """
    Tell a view to edit a string with a combo box. (Part of the model-view 
    framework.)
    
    Uses special class ``WritableCurrentTextComboBox``.
    The combo box is created, and equipped with its list of choices, by this
    class.
    
    The choices (items) can be either provided as a list of strings,
    or as a callback, that is called when the combo box is created. 
    
    This class is registered with ``QItemEditorFactory`` which is used by 
    ``QStyledItemDelegate`` which is in turn used by ``QTreeView`` or an other 
    view. ::
    
        self.v_learn_view = QTreeView()
        combo_delegate = QStyledItemDelegate()
        editor_factory = QItemEditorFactory()
        self.combo_box_creator = EditorCreatorComboBox()
        editor_factory.registerEditor(QVariant.String, self.combo_box_creator)
        combo_delegate.setItemEditorFactory(editor_factory)
        self.v_learn_view.setItemDelegateForColumn(2, combo_delegate)
    """
    def __init__(self):
        super(EditorCreatorComboBox, self).__init__()
        #List of items (optional)
        self.items = None
        #Callback to get list of items (optional)
        self.items_callback = None
        
    def setItems(self, items):
        """
        Change the items that can be selected with the combo box.
        Parameter ``items``: list[basestring]
        """
        assert isinstance(items, list)
        assert all([isinstance(s, basestring) for s in items])
        self.items = items + [u""]
    
    def setItemCallback(self, callback):
        """
        Change the callback function (or bound method) that provides this 
        object with the list of choices for the combo box.
        Parameter ``callback``: CallableType().returns(list[basestring])
        """
        self.items_callback = callback
        
    def createWidget(self, parent):
        """
        Create the ``QComboBox`` and populate the list of items.
        Called by the model-view framework.
        """
        if self.items is not None:
            items = self.items
        elif self.items_callback is not None:
            items = self.items_callback() + [u""]
        else:
            print "``EditorCreatorComboBox``: Error! " \
                  "Choices (items) for combo box undefined!"
            items = []
        combo = WritableCurrentTextComboBox(parent)
        combo.insertItems(0, items)
        combo.setEditable(True)
        return combo
    
    def valuePropertyName(self):
        """Tell which property of the combo box contains the original string."""
        return "currentText"
    
    
    
class DataWidgetHtmlView(QTabWidget):
    """
    A widget that can display HTML, and works together with 
    ``QDataWidgetMapper``
    
    The class has a property ``html``, that can be used by ``QDataWidgetMapper``
    to put HTML data into the widget.
    
    The widget has 3 tabs, that show the contents in different formats:
    * Graphically rendered HTML.
    * Pure text, with newlines at the right places.
    * HTML source code.
    """
    def __init__(self, parent=None):
        super(DataWidgetHtmlView, self).__init__(parent)
        self.html_str = None
        self.contents_loaded = [False, False, False]
        self.html_view = QWebView()
        self.text_view = QTextEdit()
        self.source_view = QTextEdit()
        
        self.addTab(self.html_view, "HTML")
        self.addTab(self.text_view, "Text")
        self.addTab(self.source_view, "Source")
        self.text_view.setReadOnly(True)
        self.source_view.setReadOnly(True)
        
        self.currentChanged.connect(self.setTabContents)
        
        
    def setTabContents(self, itab):
        """
        Sets the contents of the visible tab. Converts the contents only once.
        """
        #Only do loading and conversion operations if necessary
        if self.contents_loaded[itab]:
            return
        self.contents_loaded[itab] = True
        
        if itab == 0:
            self.html_view.setHtml(self.html_str)
        elif itab == 1:
            text = HtmlTool.to_nice_text(self.html_str)
            self.text_view.setPlainText(text)
        else:
            self.source_view.setPlainText(self.html_str)
            
        
    def getHtml(self):
        return self.html_str
    
    def setHtml(self, html_str):
        self.html_str = html_str
        self.contents_loaded = [False, False, False]
        self.setTabContents(self.currentIndex())
        
    html = pyqtProperty(str, getHtml, setHtml, 
                        doc="The html content of the widget.")
    
    
    
class ListingsEditWidget(QWidget):
    """
    Display and edit contents of a single listing.
    
    The data is taken from a row of a ``ListingsModel``. 
    The communication between the model and the individual edit widgets, 
    is done by a ``QDataWidgetMapper``.
    """
    def __init__(self):
        super(ListingsEditWidget, self).__init__()
        
        self.product_model = ProductModel()
        
        #Transfer data between model and widgets
        self.mapper = QDataWidgetMapper()
        self.learn_model = LearnDataProxyModel()
        
        bigF = QFont()
        bigF.setPointSize(12)
        
        #Create the widgets that display one listing
        self.v_id = QLabel("---")
        self.v_id.setTextInteractionFlags(Qt.TextSelectableByMouse | 
                                          Qt.TextSelectableByKeyboard)
        self.v_title = QLabel("---")
        self.v_title.setFont(bigF)
        self.v_title.setWordWrap(True)
        self.v_title.setTextInteractionFlags(Qt.TextSelectableByMouse | 
                                             Qt.TextSelectableByKeyboard)
        self.v_image = QLabel("Image\nHere!")
        self.v_price = QLabel("---")
        self.v_currency1 = QLabel("---")
        self.v_shipping = QLabel("---")
        self.v_currency2 = QLabel("---")
        self.v_type = QLabel("---")
        self.v_end_time = QLabel("0000-00-00T00:00:00")
        self.v_sold = QLabel("---")
        self.v_active = QLabel("---")
        self.v_condition = QLabel("---")
        self.v_postcode = QLabel("---")
        self.v_location = QLabel("---")
        self.v_location.setWordWrap(True)
        self.v_country = QLabel("---")
        self.v_prod_specs = QLabel("---")
        self.v_prod_specs.setWordWrap(True)
        self.v_is_training = QCheckBox("Is training sample")        
        self.v_description = DataWidgetHtmlView()
        
        #Create widget for product recognition data, and related objects
        self.v_learn_view = QTreeView()
        combo_delegate = QStyledItemDelegate()
        editor_factory = QItemEditorFactory()
        self.combo_box_creator = EditorCreatorComboBox()
        editor_factory.registerEditor(QVariant.String, self.combo_box_creator)
        combo_delegate.setItemEditorFactory(editor_factory)
        self.v_learn_view.setItemDelegateForColumn(2, combo_delegate)
        self.v_learn_view.setModel(self.learn_model)
        self.v_learn_view.setRootIsDecorated(False)
        
        l_id = QLabel("ID:")
        l_shipping = QLabel("(Shipping)")
        l_end_time = QLabel("Ends:")
        l_sold = QLabel("Sold:")
        L_active = QLabel("Active:")
        L_condition = QLabel("Condition:")
        l_location = QLabel("Location:")
        
        #Main layout
        lmain = QGridLayout()
        lmain.addWidget(self.v_title,       0, 0, 1, 3)
        lmain.addWidget(self.v_image,       1, 0, 4, 1)
        
        #Table of small values
        table = QGridLayout()
        #cols 1, 2 
        table.addWidget(self.v_price,     1, 1)
        table.addWidget(self.v_currency1, 1, 2)
        table.addWidget(self.v_shipping,  2, 1)
        table.addWidget(self.v_currency2, 2, 2)
        table.addWidget(l_sold,           3, 1)
        table.addWidget(self.v_sold,      3, 2)
        table.addWidget(L_active,         4, 1)
        table.addWidget(self.v_active,    4, 2)
        #cols 3, 4
        table.addWidget(self.v_type,      1, 3)
        table.addWidget(l_shipping,       2, 3, 1, 2)
        table.addWidget(l_end_time,       3, 3)
        table.addWidget(self.v_end_time,  3, 4)
        table.addWidget(L_condition,      4, 3)
        table.addWidget(self.v_condition, 4, 4)
        table.addWidget(l_id,             6, 3)
        table.addWidget(self.v_id,        6, 4)
        #cols 1, 2, 3, 4
        table.addWidget(l_location,       5, 1)
        table.addWidget(self.v_postcode,  5, 2)
        table.addWidget(self.v_location,  5, 3)
        table.addWidget(self.v_country,   5, 4)
        #Add table to main layout
        lmain.addLayout(table,              1, 1, 4, 2)

        lmain.addWidget(self.v_is_training, 5, 0)
        lmain.addWidget(self.v_learn_view,  6, 0, 1, 3)
        lmain.addWidget(self.v_prod_specs,  7, 0, 1, 3)
        lmain.addWidget(self.v_description, 8, 0, 2, 3)
        
        self.setLayout(lmain)
        self.setGeometry(200, 200, 400, 300)
  
        self.setToolTip('Change information about a listing.')
        self.v_id.setToolTip(Product.tool_tips["id"])

  
    def setModel(self, model):
        """Tell the widget which model it should use."""
        #Put model into communication object
        self.mapper.setModel(model)
        #Tell: which widget should show which column
        self.mapper.addMapping(self.v_id,          0, "text")
        self.mapper.addMapping(self.v_title,       8, "text")
        self.mapper.addMapping(self.v_price,      14, "text")
        self.mapper.addMapping(self.v_currency1,  13, "text")
        self.mapper.addMapping(self.v_shipping,   15, "text")
        self.mapper.addMapping(self.v_currency2,  13, "text")
        self.mapper.addMapping(self.v_sold,       12, "text")
        self.mapper.addMapping(self.v_active,     11, "text")
        self.mapper.addMapping(self.v_type,       16, "text")
        self.mapper.addMapping(self.v_end_time,   17, "text")
        self.mapper.addMapping(self.v_condition,  21, "text")
        self.mapper.addMapping(self.v_postcode,   19, "text")
        self.mapper.addMapping(self.v_location,   18, "text")
        self.mapper.addMapping(self.v_country,    20, "text")
        self.mapper.addMapping(self.v_is_training, 1, )
        self.mapper.addMapping(self.v_prod_specs, 10, "text")
        self.mapper.addMapping(self.v_description, 9, "html")
        
        self.learn_model.setSourceModel(model, 3, 4, 5)
        

    def setProductModel(self, product_model):
        """Set product model (container)."""
        self.product_model = product_model
        self.learn_model.setProductModel(product_model)
        #Put list of products into combo box 
        self.combo_box_creator.setItemCallback(
                                        self.product_model.getProductIDList)
        
        
    def setRow(self, index):
        """
        Set the row of the model that is accessed by the widget.
        
        Usually connected to signal ``activated`` of a ``QTreeView``.
        
        Parameter
        ---------
        index : QModelIndex
        """
        self.mapper.setCurrentModelIndex(index)
        self.learn_model.setRow(index)



class ListingsWidget(QSplitter):
    """
    Display and edit a list of ``Product`` objects. There is a pane that shows
    the whole list, and an other pane that shows a single product.
    
    The data is taken from a ``ProductModel``.
    """
    def __init__(self, parent=None):
        super(ListingsWidget, self).__init__(parent)
        self.edit_widget = ListingsEditWidget()
        self.list_widget = QTreeView()
        self.filter = QSortFilterProxyModel()
        
        #Assemble the child widgets
        self.addWidget(self.list_widget)
        self.addWidget(self.edit_widget)
    
        #Set various options of the view. #TODO: Delete unnecessary
        self.list_widget.setItemsExpandable(False)
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget.setDragEnabled(False)
        self.list_widget.setAcceptDrops(False)
        self.list_widget.setDropIndicatorShown(True)
        self.list_widget.setDefaultDropAction(Qt.MoveAction)
#        self.list_widget.setEditTriggers(QAbstractItemView.EditKeyPressed |
#                                         #QAbstractItemView.AnyKeyPressed |
#                                         QAbstractItemView.SelectedClicked)
        self.list_widget.setRootIsDecorated(False)
        self.list_widget.setSortingEnabled(True)
        self.list_widget.setContextMenuPolicy(Qt.ActionsContextMenu)
                
        self.filter.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.filter.setDynamicSortFilter(False)
                

    def setModel(self, model):
        """Set listings model (container). Displayed in large ``QTreeView``."""
        self.filter.setSourceModel(model)
        self.edit_widget.setModel(self.filter)
        self.list_widget.setModel(self.filter)
        #When user selects a line in ``list_widget`` this item is shown 
        #in ``edit_widget``
        self.list_widget.selectionModel().currentRowChanged.connect(
                                                        self.slotRowChanged)
    
    def setProductModel(self, product_model):
        """
        Set product model (container). 
        Displayed as additional information in ``self.edit_widget``.
        """
        self.edit_widget.setProductModel(product_model)
        
    def slotRowChanged(self, current, _previous):
        """
        The selected row has changed. Tells edit widget to show this row.
        Connected to signal ``currentRowChanged`` of 
        ``list_widget.selectionModel()``
        """
        self.edit_widget.setRow(current)
        
    def saveSettings(self, setting_store):
        """Save widget state, such as splitter position."""
        setting_store.setValue("ListingsWidget/state", self.saveState())
        setting_store.setValue("ListingsWidget/list/header/state", 
                               self.list_widget.header().saveState())
        setting_store.setValue(
                            "ListingsWidget/editor/learn_list/header/state", 
                            self.edit_widget.v_learn_view.header().saveState())
        
    def loadSettings(self, setting_store):
        """Load widget state, such as splitter position."""
        self.restoreState(setting_store.value("ListingsWidget/state", ""))
        self.list_widget.header().restoreState(
            setting_store.value("ListingsWidget/list/header/state", ""))
        self.edit_widget.v_learn_view.header().restoreState(
            setting_store.value("ListingsWidget/editor/learn_list/header/state", 
                                ""))



class ListingsModel(QAbstractTableModel):
    """
    Represent a ``pd.DataFrame`` with listings to QT's model view architecture.
    An adapter in design pattern language.
    """
    def __init__(self, parent=None):
        super(ListingsModel, self).__init__(parent)
        self.data_store = DataStore() #Dummy
    
    def setDataStore(self, data_store):
        """Put list of products into model"""
        #Tell the view(s) that old data is gone.
        rows, _ = self.data_store.listings.shape
        self.beginRemoveRows(QModelIndex(), 0, rows)
        self.endRemoveRows()
        #Change the data
        self.data_store = data_store
        #Tell the view(s) that all data has changed.
        self.layoutChanged.emit()

    def slotDataChanged(self):
        "Signal the model that the underlying data has changed."
        self.beginResetModel()
        self.endResetModel()
            
    def rowCount(self, parent=QModelIndex()):
        """Return number of products in list."""
        if parent.isValid(): #There are only top level items
            return 0
        rows, _ = self.data_store.listings.shape
        return rows
    
    def columnCount(self, parent=QModelIndex()):
        """Return number of accessible product attributes."""
        if parent.isValid(): #There are only top level items
            return 0
        _, cols = self.data_store.listings.shape
        return cols
    
    def supportedDropActions(self):
        """Say which actions are supported for drag-drop."""
        return Qt.CopyAction
 
    def flags(self, index):
        """
        Determines the possible actions for the item at this index.
        
        Parameters
        ----------
        index: QModelIndex
        """
        default_flags = super(ListingsModel, self).flags(index)
        
        if index.isValid():
            return Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | \
                   Qt.ItemIsEditable | default_flags
        else:
            return default_flags
    
    attr_names = ["id", "training_sample", "search_tasks", "expected_products", 
                  "products", "products_absent", "thumbnail", "image", 
                  "title", "description", "prod_spec", "active", "sold", 
                  "currency", "price", "shipping", "type", "time", "location", 
                  "postcode", "country", "condition", "server", "server_id", 
                  "final_price", "url_webui", "seller", "buyer"]
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Return the text for the column headers.
        
        Parameters
        -----------
        section: int
            Column number
        orientation: 
            Qt.Vertical or Qt.Horizontal
        role: int
        """
        if orientation != Qt.Horizontal or role != Qt.DisplayRole:
            return None
#        header_names = list(self.listings.columns)
        return ListingsModel.attr_names[section]


    def data(self, index, role=Qt.DisplayRole):
        """
        Return the contents of the product list in the right way.
        
        Parameters
        -----------
        index: QModelIndex
        role: int 
        """
#        assert index.model() == self
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()
        aname = ListingsModel.attr_names[column]
        
        if role == Qt.DisplayRole:
            rawval = self.data_store.listings[aname].iget(row)
            #return only first line of multi line string
            rawstr = unicode(rawval)
            lines = rawstr.split("\n", 1)
            return lines[0]
        elif role == Qt.EditRole:
            rawval = self.data_store.listings[aname].iget(row)
            if aname in ["expected_products", "products", "products_absent"]:
                return rawval
            #Special treatments for bool, because bool(nan) == True
            elif aname in ["training_sample"]:
                cooked = False if isinstance(rawval, float) and isnan(rawval) \
                         else bool(rawval)
                return cooked
            else:
                return unicode(rawval)
        #TODO: Tool tips
#        elif role == Qt.ToolTipRole:
#            aname = attr_names[column]
#            return Product.tool_tips[aname]
                        
        return None
    
    
    def setData(self, index, value, role=Qt.EditRole):
        """
        Change the data in the model.
        
        Parameters
        ----------
        index : QModelIndex
        value: object
        role : int
        
        Retuns
        ------
        bool
            Returns ``True`` if data was changed successfully, 
            returns ``False`` otherwise.
        
        TODO: Warning when ID is changed
        TODO: Special treatment of column "time": Convert string to ``datetime``
              dateutil.parser.parse(value)
        """
        assert index.model() == self
        if role != Qt.EditRole:
            return False
        if not index.isValid():
            return False
        
        row = index.row()
        column = index.column()
        aname = ListingsModel.attr_names[column]
        if value in ["nan", "None"]:
            value = None   #None is converted automatically to nan if necessary
        try:
            self.data_store.listings[aname][row] = value
        except (TypeError, ValueError):
            return False
        
        self.data_store.listings_dirty = True
        self.dataChanged.emit(index, index)
        return True
    
    
    def setItemData(self, index, roles):
        """
        Change data in model. Intention is to change data more efficiently,
        because data with with several roles is changed at once.
        
        Parameters
        ----------
        index : QModelIndex
        roles : dict[int, object]
        
        Retuns
        ------
        bool
            Returns ``True`` if data was changed successfully, 
            returns ``False`` otherwise.
        """
        #Only data with Qt.EditRole can be changed
        if Qt.EditRole not in roles:
            return False
        return self.setData(index, roles[Qt.EditRole], Qt.EditRole)



class GuiMain(QMainWindow):
    """Main window of GUI application"""
    def __init__(self, parent=None, flags=Qt.Window): 
        super(GuiMain, self).__init__(parent, flags)
        
        #Create data attributes
        self.data = DataStore()
        self.recognizers = RecognizerController()
        
        #Create the GUI components
        self.main_tabs = QTabWidget()
        self.listings_editor = ListingsWidget()
        self.listings_model = ListingsModel()
        self.product_editor = ProductWidget()
        self.product_model = ProductModel()
        self.task_editor = TaskWidget()
        self.task_model = TaskModel()
        
        #Assemble the top level widgets
        self. setCentralWidget(self.main_tabs)
        self.main_tabs.addTab(self.listings_editor, "Listings")
        self.listings_editor.setModel(self.listings_model)
        self.listings_editor.setProductModel(self.product_model)
        self.main_tabs.addTab(self.product_editor, "Products")
        self.product_editor.setModel(self.product_model, self.recognizers, 
                                     self.data)
        self.main_tabs.addTab(self.task_editor, "Tasks")
        self.task_editor.setModel(self.task_model, self.listings_model, 
                                  self.data)
        
        #For QSettings and Phonon
        QCoreApplication.setOrganizationName("The Clair Project")
        QCoreApplication.setOrganizationDomain("https://github.com/eike-welk/clair")
        QCoreApplication.setApplicationName("clairgui")
        
        self.createMenus()
        #Create the status bar
        self.statusBar()
        #Read status information that is saved on closing the application
        self.loadSettings()
        
    
    def createMenus(self):
        """Create the application's menus. Run once at start of application."""
        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")
        #TODO: better word for "configuration"
        filemenu.addAction("&Open Configuration", self.loadConfiguration, 
                           QKeySequence.Open)
        filemenu.addAction("&Save Configuration", self.saveConfiguration, 
                           QKeySequence.Save)
        filemenu.addAction("&Quit", self.close, QKeySequence.Quit)
        filemenu.addAction("Clear Settings", self.clearSettings)
        _listingmenu = menubar.addMenu("&Listing")
        productmenu = menubar.addMenu("&Product")
        productmenu.addAction(self.product_editor.action_new)
        productmenu.addAction(self.product_editor.action_delete)
        taskmenu = menubar.addMenu("&Task")
        taskmenu.addAction(self.task_editor.action_new)
        taskmenu.addAction(self.task_editor.action_delete)
        taskmenu.addSeparator()
        taskmenu.addAction(self.task_editor.action_update_expected_products)
        taskmenu.addAction(self.task_editor.action_set_expected_products)


    def askSaveModifiedFiles(self):
        """
        Test if files are modified. Ask if user wants to save modified files.
        
        Returns
        -------
        str
            The return code indicates what button the user has clicked, and 
            what action has been taken. The function returns the following 
            strings:
            * "files-saved" : There were modified files, a dialog was shown,
                              the user has clicked the "Save" button, and the 
                              files have been saved.
            * "discard"     : The user wants to discard the modified files. 
            * "cancel"      : The user has clicked the "Cancel" button and
                              wants to abort the operation.
            * "all-clean"   : There are no modified files, no dialog has been
                              shown.
        """
        if any([self.data.listings_dirty, self.data.products_dirty,
                self.data.tasks_dirty, self.recognizers.dirty]):
            button = QMessageBox.warning(
                self, "Clair Gui",
                "The data has been modified.\nDo you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save)
            if button == QMessageBox.Save:
                self.saveConfiguration()
                return "files-saved"
            elif button == QMessageBox.Discard:
                return "discard"
            else:
                return "cancel"
        else:
            return "all-clean"


    def loadConfiguration(self, dirname=None):
        """
        Load all data files of a Clair installation.
        
        Parameter
        ---------
        dirname : basestring
            Name of dir where the files are that should be loaded.
            If ``dirname`` is None, the method will go to interactive mode
            and show dialogs. Otherwise it will unconditionally load the data.
        """
        if dirname is None:
            #Interactive mode
            #If there are unsaved changes, ask user, save changes if desired.
            action = self.askSaveModifiedFiles()
            if action == "cancel":
                return
            #Show file open dialog.
            filename = QFileDialog.getOpenFileName(
                self, "Open Configuration, click on any file", os.getcwd(), "")
            #Do nothing if user has pressed the cancel button.
            if not filename:
                return
            dirname = os.path.dirname(filename)
            
        #Load the data
        self.data.read_data(dirname)
        self.recognizers.read_recognizers(dirname)
        #Put data into GUI
        self.listings_model.setDataStore(self.data)
        self.product_model.setDataStore(self.data)
        self.task_model.setDataStore(self.data)
        
        
    def saveConfiguration(self):
        """Save all data files of a Clair installation."""
        self.data.write_listings()
        self.data.write_products()
        self.data.write_tasks()
        self.recognizers.write_recognizers()
        self.statusBar().showMessage("Configuration saved.", 5000)
    
    def closeEvent(self, event):
        """Framework tells application that it wants to exit the program."""
        #If there are unsaved changes, ask user, save changes if desired.
        action = self.askSaveModifiedFiles()
        if action == "cancel":
            event.ignore()
            return
        self.saveSettings()
        super(GuiMain, self).closeEvent(event)
        
    def saveSettings(self):
        """Save application state information like window position."""
        settings = QSettings()
        #Save GUI related information
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        self.listings_editor.saveSettings(settings)
        self.product_editor.saveSettings(settings)
        self.task_editor.saveSettings(settings)
        #Save directory of current data
        settings.setValue("conf_dir", self.data.data_dir)
 
    def loadSettings(self):
        """Read application state information like window position."""
        setting_store = QSettings()
        #Load GUI related information
        self.restoreGeometry(setting_store.value("geometry", ""))
        self.restoreState(setting_store.value("windowState", ""))
        self.listings_editor.loadSettings(setting_store)
        self.product_editor.loadSettings(setting_store)
        self.task_editor.loadSettings(setting_store)
        #Load last used data
        conf_dir = setting_store.value("conf_dir", None)
        if conf_dir is not None and os.path.isdir(conf_dir):
            self.loadConfiguration(conf_dir)
 
    def clearSettings(self):
        """Deletes all settings, and restarts the application"""
        #If there are unsaved changes ask user, save changes if desired.
        action = self.askSaveModifiedFiles()
        if action == "cancel":
            return
        #Clear the settings
        setting_store = QSettings()
        setting_store.clear()
        setting_store.sync()
        #Exit application, and restart it
        QApplication.exit(GuiMain.restart_code)

    restart_code = 1000
    
    @staticmethod
    def application_main():
        """
        The application's main function. 
        Create application and main window and run them.
        """
        while True:
            app = QApplication(sys.argv)
            window = GuiMain()
            window.show()
            ret = app.exec_()
            if ret != GuiMain.restart_code:
                break
            del window
            del app
