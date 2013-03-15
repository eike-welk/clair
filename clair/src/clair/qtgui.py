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

import dateutil
import pandas as pd
from PyQt4.QtCore import (Qt, pyqtSignal, pyqtProperty, QModelIndex, 
                          QAbstractTableModel, QSettings, QCoreApplication)
from PyQt4.QtGui import (QWidget, QLabel, QLineEdit, QTextEdit, QSplitter, 
                         QMainWindow, QTabWidget, QApplication, QFileDialog,
                         QGridLayout, QTreeView, QAbstractItemView, QAction,
                         QDataWidgetMapper, QSortFilterProxyModel, QKeySequence,
                         QItemSelectionModel, QMessageBox, QFont,)
from PyQt4.QtWebKit import QWebView

from clair.coredata import make_listing_frame, Product, SearchTask, DataStore
from clair.textprocessing import HtmlTool



def QtLoadUI(uifile):
    from PyQt4 import uic
    return uic.loadUi(uifile)



def to_text_time(time):
    """Convert ``datetime`` to text in safe way."""
    try:
        return time.isoformat(" ")
    except ValueError:
        return "Date Error: " + repr(time)
    
    
    
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
        
        self.e_id = QLineEdit()
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
        grid.addWidget(self.e_id,          0, 1, 1, 3)
        grid.addWidget(l_name,             1, 0)
        grid.addWidget(self.e_name,        1, 1, 1, 3)
        grid.addWidget(l_categories,       2, 0, 1, 2)
        grid.addWidget(self.e_categories,  3, 0, 2, 2)
        grid.addWidget(l_important_words,  2, 2, 1, 2)
        grid.addWidget(self.e_important_words,3, 2, 2, 2)
        grid.addWidget(l_description,      5, 0, 1, 4)
        grid.addWidget(self.e_description, 6, 0, 2, 4)

        self.setLayout(grid)
        self.setGeometry(200, 200, 400, 300)
  
        self.setToolTip('Change information about a product.')
        self.e_id.setToolTip(Product.tool_tips["id"])
        self.e_name.setToolTip(Product.tool_tips["name"])
        self.e_important_words.setToolTip(Product.tool_tips["important_words"])
        self.e_categories.setToolTip(Product.tool_tips["categories"])
        self.e_description.setToolTip(Product.tool_tips["description"])

  
    def setModel(self, model):
        """Tell the widget which model it should use."""
        #Put model into communication object
        self.mapper.setModel(model)
        #Tell: which widget should show which column
        self.mapper.addMapping(self.e_id, 0)
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
    the list a whole, and an other pane that shows a single product.
    
    The data is taken from a ``ProductModel``.
    """
    def __init__(self, parent=None):
        super(ProductWidget, self).__init__(parent)
        self.edit_widget = ProductEditWidget()
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
        self.list_widget.setEditTriggers(QAbstractItemView.EditKeyPressed |
                                         #QAbstractItemView.AnyKeyPressed |
                                         QAbstractItemView.SelectedClicked)
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
        

    def setModel(self, model):
        """Tell view which model it should display and edit."""
        self.filter.setSourceModel(model)
        self.edit_widget.setModel(self.filter)
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
        
    def loadSettings(self, setting_store):
        """Load widget state, such as splitter position."""
        self.restoreState(setting_store.value("ProductWidget/state", ""))
        self.list_widget.header().restoreState(
                setting_store.value("ProductWidget/list/header/state", ""))
        #Hide description. TODO: remove this hack
        self.list_widget.hideColumn(4)



class ProductModel(QAbstractTableModel):
    """
    Represent a list of ``Product`` objects to QT's model view architecture.
    An adapter in design pattern language.
    """
    def __init__(self, parent=None):
        super(ProductModel, self).__init__(parent)
        self.products = []
        self.dirty = False
    
    def setProducts(self, products):
        """Put list of products into model"""
        #Tell the view(s) that old data is gone.
        self.beginRemoveRows(QModelIndex(), 0, len(self.products))
        self.endRemoveRows()
        #Change the data
        self.products = products
        self.dirty = False
        #Tell the view(s) that all data has changed.
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()):
        """Return number of products in list."""
        if parent.isValid(): #There are only top level items
            return 0
        return len(self.products)
    
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


    def data(self, index, role=Qt.DisplayRole):
        """
        Return the contents of the product list in the right way.
        
        Parameters
        -----------
        index: QModelIndex
        role: int 
        """
        assert index.model() == self
        attr_names = ["id", "name", "categories", "important_words", 
                      "description"]

        row = index.row()
        column = index.column()
        
        if role in [Qt.DisplayRole, Qt.EditRole]:
            prod = self.products[row]
            if column == 0:
                return prod.id
            elif column == 1:
                return prod.name
            elif column == 2:
                return u"\n".join(prod.categories)
            elif column == 3:
                return u"\n".join(prod.important_words)
            elif column == 4:
                return prod.description
        elif role == Qt.ToolTipRole:
            aname = attr_names[column]
            return Product.tool_tips[aname]
                        
        return None
    
    
    def setData(self, index, value, role=Qt.EditRole):
        """
        Change the data in the model.
        
        Parameters
        ----------
        index : QModelIndex
        value: object
        role : int
        
        TODO: Warning when ID is changed
        """
        assert index.model() == self
        if role != Qt.EditRole:
            return False
        if not index.isValid():
            return False
        
        row = index.row()
        column = index.column()
        prod = self.products[row]
        if column == 0:
            prod.id = value
        elif column == 1:
            prod.name = value
        elif column == 2:
            val_list = value.split("\n")
            prod.categories = val_list
        elif column == 3:
            val_list = value.split("\n")
            prod.important_words = val_list
        elif column == 4:
            prod.description = value
            
        self.dirty = True
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
            self.products.insert(row + i, new_prod)
        self.endInsertRows()
        
        self.dirty = True
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
        del self.products[row:row + count]
        self.endRemoveRows()
        
        self.dirty = True
        return True



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
#        l_currency = QLabel("Currency")
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
    the list a whole, and an other pane that shows a single product.
    
    The data is taken from a ``ProductModel``.
    """
    def __init__(self, parent=None):
        super(TaskWidget, self).__init__(parent)
        self.edit_widget = SearchTaskEditWidget()
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
        self.list_widget.setEditTriggers(QAbstractItemView.EditKeyPressed |
                                         #QAbstractItemView.AnyKeyPressed |
                                         QAbstractItemView.SelectedClicked)
        self.list_widget.setRootIsDecorated(False)
        self.list_widget.setSortingEnabled(True)
        self.list_widget.setContextMenuPolicy(Qt.ActionsContextMenu)
        
        #Create context menu for list view
        self.action_new = QAction("&New Task", self)
        self.action_new.setShortcuts(QKeySequence.InsertLineSeparator)
        self.action_new.setToolTip(
                                "Create new task below selected task.")
        self.action_new.triggered.connect(self.newProduct)
        self.list_widget.addAction(self.action_new)
        self.action_delete = QAction("&Delete Task", self)
        self.action_delete.setShortcuts(QKeySequence.Delete)
        self.action_delete.setToolTip("Delete selected task.")
        self.action_delete.triggered.connect(self.deleteProduct)
        self.list_widget.addAction(self.action_delete)
        
        self.filter.setSortCaseSensitivity(Qt.CaseInsensitive)
        

    def setModel(self, model):
        """Tell view which model it should display and edit."""
        self.filter.setSourceModel(model)
        self.edit_widget.setModel(self.filter)
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
        setting_store.setValue("TaskWidget/state", self.saveState())
        setting_store.setValue("TaskWidget/list/header/state", 
                               self.list_widget.header().saveState())
        
    def loadSettings(self, setting_store):
        """Load widget state, such as splitter position."""
        self.restoreState(setting_store.value("TaskWidget/state", ""))
        self.list_widget.header().restoreState(
                setting_store.value("TaskWidget/list/header/state", ""))
        #Hide multi line attribute expected products. TODO: remove this hack
        self.list_widget.hideColumn(9)



class TaskModel(QAbstractTableModel):
    """
    Represent a list of tasks (currently only ``SearchTask``) to QT's model 
    view architecture.
    An adapter in design pattern language.
    """
    def __init__(self, parent=None):
        super(TaskModel, self).__init__(parent)
        self.tasks = []
        self.dirty = False
    
    def setTasks(self, tasks):
        """Put list of tasks into model"""
        #Tell the view(s) that old data is gone.
        self.beginRemoveRows(QModelIndex(), 0, len(self.tasks))
        self.endRemoveRows()
        #Change the data
        self.tasks = tasks
        self.dirty = False
        #Tell the view(s) that all data has changed.
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()):
        """Return number of tasks in list."""
        if parent.isValid(): #There are only top level items
            return 0
        return len(self.tasks)
    
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
        assert index.model() == self
        attr_names = TaskModel.attr_names

        row = index.row()
        column = index.column()
        
        if role in [Qt.DisplayRole, Qt.EditRole]:
            task = self.tasks[row]
            attr_name = attr_names[column]
            if attr_name == "due_time":
                return to_text_time(task.due_time)
            elif attr_name == "expected_products":
                return u"\n".join(task.expected_products)
            else:
                return getattr(task, attr_name)
        elif role == Qt.ToolTipRole:
            aname = attr_names[column]
            return SearchTask.tool_tips[aname]
                        
        return None
    
    
    def setData(self, index, value, role=Qt.EditRole):
        """
        Change the data in the model.
        
        Parameters
        ----------
        index : QModelIndex
        value: object
        role : int
        
        TODO: Warning when ID is changed
        """
        assert index.model() == self
        if role != Qt.EditRole:
            return False
        if not index.isValid():
            return False
        
        row = index.row()
        column = index.column()
        task = self.tasks[row]
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
        
        self.dirty = True
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
            self.tasks.insert(row + i, new_prod)
        self.endInsertRows()
        
        self.dirty = True
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
        del self.tasks[row:row + count]
        self.endRemoveRows()
        
        self.dirty = True
        return True



class DataWidgetHtmlView(QTabWidget):
    """
    A widget that can display HTML, and works together with 
    ``QDataWidgetMapper``
    
    The class has a property ``html``, that can be used by ``QDataWidgetMapper``
    to put HTML data into the widget.
    
    TODO: convert to a tab widget that can alternatively show a pure text view.
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
        
        bigF = QFont()
        bigF.setPointSize(12)
        
        #Transfers data between model and widgets
        self.mapper = QDataWidgetMapper()
        
        self.v_id = QLabel("---")
        self.v_id.setTextInteractionFlags(Qt.TextSelectableByMouse | 
                                          Qt.TextSelectableByKeyboard)
        self.v_title = QLabel("---")
        self.v_title.setFont(bigF)
        self.v_title.setWordWrap(True)
        self.v_title.setTextInteractionFlags(Qt.TextSelectableByMouse | 
                                             Qt.TextSelectableByKeyboard)
        self.v_image = QLabel("Image\nHere!")
        self.v_price = QLabel("xxx")
        self.v_currency1 = QLabel("---")
        self.v_shipping = QLabel("xxx")
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
        self.v_description = DataWidgetHtmlView()
        
        l_id = QLabel("ID")
        l_shipping = QLabel("(Shipping)")
        l_end_time = QLabel("Ends")
        l_sold = QLabel("Sold")
        L_active = QLabel("Active")
        L_condition = QLabel("Condition")
        l_location = QLabel("Location")
        
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

        lmain.addWidget(self.v_prod_specs,  5, 0, 1, 3)
        lmain.addWidget(self.v_description, 6, 0, 2, 3)
        
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
        self.mapper.addMapping(self.v_prod_specs, 10, "text")
        self.mapper.addMapping(self.v_description, 9, "html")
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



class ListingsWidget(QSplitter):
    """
    Display and edit a list of ``Product`` objects. There is a pane that shows
    the list a whole, and an other pane that shows a single product.
    
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
        self.list_widget.setEditTriggers(QAbstractItemView.EditKeyPressed |
                                         #QAbstractItemView.AnyKeyPressed |
                                         QAbstractItemView.SelectedClicked)
        self.list_widget.setRootIsDecorated(False)
        self.list_widget.setSortingEnabled(True)
        self.list_widget.setContextMenuPolicy(Qt.ActionsContextMenu)
                
        self.filter.setSortCaseSensitivity(Qt.CaseInsensitive)
                

    def setModel(self, model):
        """Tell view which model it should display and edit."""
        self.filter.setSourceModel(model)
        self.edit_widget.setModel(self.filter)
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
        
    def saveSettings(self, setting_store):
        """Save widget state, such as splitter position."""
        setting_store.setValue("ListingsWidget/state", self.saveState())
        setting_store.setValue("ListingsWidget/list/header/state", 
                               self.list_widget.header().saveState())
        
    def loadSettings(self, setting_store):
        """Load widget state, such as splitter position."""
        self.restoreState(setting_store.value("ListingsWidget/state", ""))
        self.list_widget.header().restoreState(
                setting_store.value("ListingsWidget/list/header/state", ""))



class ListingsModel(QAbstractTableModel):
    """
    Represent a ``pd.DataFrame`` with listings to QT's model view architecture.
    An adapter in design pattern language.
    """
    def __init__(self, parent=None):
        super(ListingsModel, self).__init__(parent)
        self.listings = make_listing_frame(0)
        self.dirty = False
    
    def setListings(self, listings):
        """Put list of products into model"""
        #Tell the view(s) that old data is gone.
        rows, _ = self.listings.shape
        self.beginRemoveRows(QModelIndex(), 0, rows)
        self.endRemoveRows()
        #Change the data
        self.listings = listings
        self.dirty = False
        #Tell the view(s) that all data has changed.
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()):
        """Return number of products in list."""
        if parent.isValid(): #There are only top level items
            return 0
        rows, _ = self.listings.shape
        return rows
    
    def columnCount(self, parent=QModelIndex()):
        """Return number of accessible product attributes."""
        if parent.isValid(): #There are only top level items
            return 0
        _, cols = self.listings.shape
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
    
    attr_names = ['id', 'training_sample', 'search_task', 'expected_products', 
                  'products', 'products_absent', 'thumbnail', 'image', 
                  'title', 'description', 'prod_spec', 'active', 'sold', 
                  'currency', 'price', 'shipping', 'type', 'time', 'location', 
                  'postcode', 'country', 'condition', 'server', 'server_id', 
                  'final_price', 'url_webui']
    
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
        assert index.model() == self

        row = index.row()
        column = index.column()
        aname = ListingsModel.attr_names[column]
        
        if role == Qt.DisplayRole:
            rawval = self.listings[aname].iget(row)
            rawstr = unicode(rawval)
            lines = rawstr.split("\n", 1)
            return lines[0]
        elif role == Qt.EditRole:
            rawval = self.listings[aname].iget(row)
            rawstr = unicode(rawval)
            return rawstr
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
        
        TODO: Warning when ID is changed
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
            self.listings[aname][row] = value
        except (TypeError, ValueError):
            return False
            
        self.dirty = True
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
        self.main_tabs.addTab(self.product_editor, "Products")
        self.product_editor.setModel(self.product_model)
        self.main_tabs.addTab(self.task_editor, "Tasks")
        self.task_editor.setModel(self.task_model)
        
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
        if any([self.listings_model.dirty, self.product_model.dirty,
                self.task_model.dirty]):
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
            dirname = os.path.dirname(filename)
            
        #Load the data
        self.data.products = {}
        self.data.tasks = {}
        self.data.listings = pd.DataFrame()
        self.data.read_data(dirname)
        self.listings_model.setListings(self.data.listings)
        self.product_model.setProducts(self.data.products.values())
        self.task_model.setTasks(self.data.tasks.values())
        
        
    def saveConfiguration(self):
        """Save all data files of a Clair installation."""
        #save listings
        self.data.write_listings()
        self.listings_model.dirty = False
        #save products
        self.data.products = {}
        self.data.add_products(self.product_model.products)
        self.data.write_products()
        self.product_model.dirty = False
        #save tasks
        self.data.tasks={}
        self.data.add_tasks(self.task_model.tasks)
        self.data.write_tasks()
        self.task_model.dirty = False
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
