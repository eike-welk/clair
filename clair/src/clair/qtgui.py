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
#from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import (Qt, pyqtSignal,  QModelIndex, QAbstractTableModel, 
                          QSettings, QCoreApplication)
from PyQt4.QtGui import (QWidget, QLabel, QLineEdit, QTextEdit, QSplitter, 
                         QMainWindow, QTabWidget, QApplication, QFileDialog,
                         QGridLayout, QTreeView, QAbstractItemView, QAction,
                         QDataWidgetMapper, QSortFilterProxyModel, QKeySequence,
                         QItemSelectionModel, QMessageBox)
import sys
import os

import pandas as pd

from clair.coredata import make_listing_frame, Product, DataStore



def QtLoadUI(uifile):
    from PyQt4 import uic
    return uic.loadUi(uifile)



class ProductWidget(QWidget):
    """
    Display and edit contents of a single ``Product``.
    
    The data is taken from a row of a ``ProductModel``. 
    The communication between the model and the individual edit widgets, 
    is done by a ``QDataWidgetMapper``.  
    
    TODO: Important words and categories should be less high
    """
    def __init__(self):
        super(ProductWidget, self).__init__()
        
        #Transfer data between model and widgets
        self.mapper = QDataWidgetMapper()
        
        self.e_id = QLineEdit()
        self.e_name = QLineEdit()
        self.e_description = QTextEdit()
        self.e_important_words = QTextEdit()
        self.e_categories = QTextEdit()
        
        l_id = QLabel("ID")
        l_name = QLabel("Name")
        l_description = QLabel("Description")
        l_important_words = QLabel("Important \nWords")
        l_categories = QLabel("Categories")
        
        grid = QGridLayout()
        grid.addWidget(l_id, 0, 0)
        grid.addWidget(self.e_id, 0, 1)
        grid.addWidget(l_name, 1, 0)
        grid.addWidget(self.e_name, 1, 1)
        grid.addWidget(l_important_words, 2, 0)
        grid.addWidget(self.e_important_words,2, 1)
        grid.addWidget(l_categories, 3, 0)
        grid.addWidget(self.e_categories, 3, 1)
        grid.addWidget(l_description, 4, 0, 1, 2)
        grid.addWidget(self.e_description, 5, 0, 4, 2)

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



class ProductListWidget(QSplitter):
    """
    Display and edit a list of ``Product`` objects. There is a pane that shows
    the list a whole, and an other pane that shows a single product.
    
    The data is taken from a ``ProductModel``.
    """
    def __init__(self, parent=None):
        super(ProductListWidget, self).__init__(parent)
        self.edit_widget = ProductWidget()
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
        self.action_delete.setStatusTip("Delete selected product")
        self.action_delete.triggered.connect(self.deleteProduct)
        self.list_widget.addAction(self.action_delete)
        
        self.filter.setSortCaseSensitivity(Qt.CaseInsensitive)
        

    def setModel(self, model):
        """Tell view which model it should display and edit."""
        self.filter.setSourceModel(model)
        self.edit_widget.setModel(self.filter)
        self.list_widget.setModel(self.filter)
        #Hide the description and sort by ID
        self.list_widget.hideColumn(4)
        self.list_widget.sortByColumn(0, Qt.AscendingOrder)
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



class ListingsListWidget(QSplitter):
    """
    Display and edit a list of ``Product`` objects. There is a pane that shows
    the list a whole, and an other pane that shows a single product.
    
    The data is taken from a ``ProductModel``.
    """
    def __init__(self, parent=None):
        super(ListingsListWidget, self).__init__(parent)
        self.edit_widget = None
        self.list_widget = QTreeView()
        self.filter = QSortFilterProxyModel()
        
        #Assemble the child widgets
        self.addWidget(self.list_widget)
#        self.addWidget(self.edit_widget)
    
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
#        self.edit_widget.setModel(self.filter)
        self.list_widget.setModel(self.filter)
        #Hide the description and sort by ID
        self.list_widget.hideColumn(4)
        self.list_widget.sortByColumn(0, Qt.AscendingOrder)
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
#        self.edit_widget.setRow(current)



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
        header_names = list(self.listings.columns)
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

        row = index.row()
        column = index.column()
        
        if role in [Qt.DisplayRole, Qt.EditRole]:
            rawval = self.listings.icol(column).iget(row)
            rawstr = unicode(rawval)
            lines = rawstr.split("\n", 1)
            return lines[0]
            
        
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
        if value in ["nan", "None"]:
            value = None             #None is converted to nan if necessary
        try:
            self.listings.icol(column)[row] = value
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
        self.product_editor = ProductListWidget()
        self.product_model = ProductModel()
        self.listings_editor = ListingsListWidget()
        self.listings_model = ListingsModel()
        
        #Assemble the top level widgets
        self. setCentralWidget(self.main_tabs)
        self.main_tabs.addTab(self.listings_editor, "Listings")
        self.listings_editor.setModel(self.listings_model)
        self.main_tabs.addTab(self.product_editor, "Products")
        self.product_editor.setModel(self.product_model)
        
        #For QSettings and Phonon
        QCoreApplication.setOrganizationName("The Clair Project")
        QCoreApplication.setOrganizationDomain("https://github.com/eike-welk/clair")
        QCoreApplication.setApplicationName("clairgui")
        
        self.createMenus()
        #Create the status bar
        self.statusBar()
        #Read status information that is saved on closing the application
        self.readSettings()
        
    
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
        productmenu = menubar.addMenu("&Product")
        productmenu.addAction(self.product_editor.action_new)
        productmenu.addAction(self.product_editor.action_delete)

        
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
            if any([self.product_model.dirty]):
                button = QMessageBox.warning(
                    self, "Clair Gui",
                    "The data has been modified.\n"
                    "Do you want to save your changes?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    QMessageBox.Save)
                if button == QMessageBox.Save:
                    self.saveConfiguration()
                elif button == QMessageBox.Discard:
                    pass
                else:
                    return
            filename = QFileDialog.getOpenFileName(
                                self, "Open Configuration", os.getcwd(), "")
            dirname = os.path.dirname(filename)
            
        #Load the data
        self.data.products = {}
        self.data.tasks = {}
        self.data.listings = pd.DataFrame()
        self.data.read_data(dirname)
        self.listings_model.setListings(self.data.listings)
        self.product_model.setProducts(self.data.products.values())
        
        
    def saveConfiguration(self):
        """Save all data files of a Clair installation."""
        self.data.products = {}
        self.data.add_products(self.product_model.products)
        self.data.write_products()
        self.product_model.dirty = False
        self.statusBar().showMessage("Configuration saved.", 5000)
    
    
    def closeEvent(self, event):
        #Save modified data before closing.
        if any([self.product_model.dirty]):
            button = QMessageBox.warning(
                self, "Clair Gui",
                "The data has been modified.\nDo you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save)
            if button == QMessageBox.Save:
                self.saveConfiguration()
            elif button == QMessageBox.Discard:
                pass
            else:
                event.ignore()
                return
        
        #Save settings, 
        settings = QSettings()
        #Save window size and position
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        #Save directory of current data
        settings.setValue("conf_dir", self.data.data_dir)
        super(GuiMain, self).closeEvent(event)
 
 
    def readSettings(self):
        """
        Read application state information, that was saved in ``closeEvent``.
        """
        settings = QSettings()
        #Load window size and position
        self.restoreGeometry(settings.value("geometry"))
        self.restoreState(settings.value("windowState"))
        #Load last used data
        conf_dir = settings.value("conf_dir", None)
        if conf_dir is not None and os.path.isdir(conf_dir):
            self.loadConfiguration(conf_dir)
        
 
    @staticmethod
    def application_main():
        """
        The application's main function. 
        Create application and main window and run them.
        """
        app = QApplication(sys.argv)
        window = GuiMain()
        window.show()
        app.exec_()
