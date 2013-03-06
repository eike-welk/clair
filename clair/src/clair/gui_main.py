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
from PyQt4.QtCore import (Qt, pyqtSignal, QAbstractTableModel, QModelIndex,)
from PyQt4.QtGui import (QWidget, QLabel, QLineEdit, QTextEdit, QGridLayout,)
from clair.coredata import Product



def QtLoadUI(uifile):
    from PyQt4 import uic
    return uic.loadUi(uifile)



class ProductWidget(QWidget):
    """
    Display and change contents of a ``Product``.
    
    TODO: Important words and categories should be less high
    TODO: Warning when ID is changed
    """
    def __init__(self):
        super(ProductWidget, self).__init__()
        
        l_id = QLabel("ID")
        l_name = QLabel("Name")
        l_description = QLabel("Description")
        l_important_words = QLabel("Important \nWords")
        l_categories = QLabel("Categories")
        
        self.e_id = QLineEdit()
        self.e_name = QLineEdit()
        self.e_description = QTextEdit()
        self.e_important_words = QTextEdit()
        self.e_categories = QTextEdit()
        
        #If any contents changes, this widget emits signal ``contents_changed``
        self.e_id.textChanged.connect(self.slot_text_changed0)
        self.e_name.textChanged.connect(self.slot_text_changed0)
        self.e_description.textChanged.connect(self.slot_text_changed1)
        self.e_important_words.textChanged.connect(self.slot_text_changed1)
        self.e_categories.textChanged.connect(self.slot_text_changed1)
      
        grid = QGridLayout()
#        grid.setSpacing(10)
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
      
        
    def slot_text_changed0(self, _):
        "QLineEdit widgets connect to this slot."
        self.contents_changed.emit()
        
    def slot_text_changed1(self):
        "QTextEdit widgets connect to this slot."
        self.contents_changed.emit()
    
    contents_changed = pyqtSignal()
    "Signal that the the product information has changed." 
    
    def set_contents(self, prod):
        """Put product information into widget."""
        self.e_id.setText(prod.id)
        self.e_name.setText(prod.name)
        self.e_description.setPlainText(prod.description)
        
        important_words_text = "\n".join(prod.important_words)
        self.e_important_words.setPlainText(important_words_text)
        
        categories_text = "\n".join(prod.categories)
        self.e_categories.setPlainText(categories_text)
        
        
    def get_contents(self):
        """Retrieve product information from this widget."""
        important_words_list = self.e_important_words.toPlainText().split("\n")
        categories_list = self.e_categories.toPlainText().split("\n")
        
        return Product(id=self.e_id.text(), 
                       name=self.e_name.text(), 
                       description=self.e_description.toPlainText(),
                       important_words=important_words_list, 
                       categories=categories_list)



class ProductController(object):
    """Control Editing of ``Product`` objects."""
    def __init__(self):
        self.edit_widget = ProductWidget()
        self.list_widget = None
        self.products = []
        
        self.index = 0
        self.item_changed = False
        
        
    def edit_at(self, index):
        """Edit item at a specific index"""
        if index == self.index:
            return
        if self.item_changed:
            mod_item = self.edit_widget.get_contents()
            self.change_item(self.index, mod_item) 
        
        new_item = self.get_item(index)
        self.edit_widget.set_contents(new_item)
    
    
    def slot_current_item_changed(self):
        """Called by editor widget when when its contents changes"""
        self.item_changed = True
        
    def change_item(self, index, new_item):
        """
        Change item at index to ``new_item``.
        TODO: Undo redo facility. 
        """
        self.products[index] = new_item
    
    def get_item(self, index):
        """Retrieve item at index from list"""
        return self.products[index]



class ProductModel(QAbstractTableModel):
    """
    Represent a list of ``Product`` objects to QT's model view architecture.
    """
    def __init__(self, parent=None):
        super(ProductModel, self).__init__(parent)
        self.products = []
    
    def setProducts(self, products):
        """Put list of products into model TODO: emit necessary signals."""
        self.products = products

    #rowCount(), columnCount(), and data()
    def rowCount(self, parent):
        """Return number of products in list."""
        if parent.model() == self:
            return 0
        return len(self.products)
    
    def columnCount(self, parent):
        """Return number of accessible product attributes."""
        if parent.model() == self:
            return 0
        return 5
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        Return the text for the column headers.
        
        Parameters
        -----------
        section: int
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
        
        if role == Qt.DisplayRole:
            prod = self.products[row]
            if column == 0:
                return prod.id
            elif column == 1:
                return prod.name
            elif column == 2:
                return prod.categories[0]
            elif column == 3:
                return prod.important_words[0]
            elif column == 4:
                return prod.description
        elif role == Qt.EditRole:
            prod = self.products[row]
            if column == 0:
                return prod.id
            elif column == 1:
                return prod.name
            elif column == 2:
                return "\n".join(prod.categories)
            elif column == 3:
                return "\n".join(prod.important_words)
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
        """
        assert index.model() == self
        if role != Qt.EditRole:
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
        
        self.dataChanged.emit(index, index)
        return True
    
    
    def flags (self, index):
        """
        Determines the possible actions for the item at this index.
        
        Parameters
        ----------
        index: QModelIndex
        """
        assert index.model() == self
        return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled

