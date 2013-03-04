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
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QWidget, QLabel, QLineEdit, QTextEdit, QGridLayout

from clair.coredata import Product



def QtLoadUI(uifile):
    from PyQt4 import uic
    return uic.loadUi(uifile)



class ProductWidget(QWidget):
    """
    Display and change contents of a ``Product``.
    
    TODO: Warning when ID is changed
    """
    contents_changed = QtCore.pyqtSignal()
    
    def __init__(self):
        super(ProductWidget, self).__init__()
            
        l_id = QLabel("ID")
        l_name = QLabel("Name")
        l_description = QLabel("Description")
        self.e_id = QLineEdit()
        self.e_name = QLineEdit()
        self.e_description = QTextEdit()
        self.important_words = None
        self.categories = None
        
        self.e_id.textChanged.connect(self.slot_text_changed0)
        self.e_name.textChanged.connect(self.slot_text_changed0)
        self.e_description.textChanged.connect(self.slot_text_changed1)
      
        grid = QtGui.QGridLayout()
#        grid.setSpacing(10)
        grid.addWidget(l_id, 0, 0)
        grid.addWidget(self.e_id, 0, 1)
        grid.addWidget(l_name, 1, 0)
        grid.addWidget(self.e_name, 1, 1)
        grid.addWidget(l_description, 2, 0, 1, 2)
        grid.addWidget(self.e_description, 3, 0, 6, 2)

        self.setLayout(grid)
        self.setGeometry(200, 200, 400, 300)
        
        
    def slot_text_changed0(self, _):
        self.contents_changed.emit()
#        print "Text changed 0!"
        
    def slot_text_changed1(self):
        self.contents_changed.emit()
#        print "Text changed 1!"
        
    
    def set_Product(self, prod):
        """Put product information into widget."""
        self.e_id.setText(prod.id)
        self.e_name.setText(prod.name)
        self.e_description.setText(prod.description)
        self.important_words = prod.important_words
        self.categories = prod.categories
        
        

class Example(QtGui.QWidget):
    
    closeApp = QtCore.pyqtSignal()
        
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()
       
        
    def initUI(self):
        self.setToolTip('This is a <b>QWidget</b> widget')
        
#        okButton = QtGui.QPushButton("OK")
#        cancelButton = QtGui.QPushButton("Cancel")
#
#        hbox = QtGui.QHBoxLayout()
#        hbox.addStretch(1)
#        hbox.addWidget(okButton)
#        hbox.addWidget(cancelButton)
#
#        vbox = QtGui.QVBoxLayout()
#        vbox.addStretch(1)
#        vbox.addLayout(hbox)
#        
#        self.setLayout(vbox)    
#        
#        self.setGeometry(300, 300, 300, 150)
#        self.setWindowTitle('Buttons')

        title = QtGui.QLabel('Title')
        author = QtGui.QLabel('Author')
        review = QtGui.QLabel('Review')

        titleEdit = QtGui.QLineEdit()
        authorEdit = QtGui.QLineEdit()
        reviewEdit = QtGui.QTextEdit()

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(title, 1, 0)
        grid.addWidget(titleEdit, 1, 1)

        grid.addWidget(author, 2, 0)
        grid.addWidget(authorEdit, 2, 1)

        grid.addWidget(review, 3, 0)
        grid.addWidget(reviewEdit, 3, 1, 5, 1)
        
        self.setLayout(grid) 
        
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Review')    

        titleEdit.textChanged.connect(self.print_text)
        

    def print_text(self, text):
        print str(text)
    
    def print_true(self):
        print "true"
