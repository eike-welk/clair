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
Text processing and machine learning.
"""

from __future__ import division
from __future__ import absolute_import              

import re 

import lxml.html


class RemoveHTML(object):
    """Remove any HTML markup and convert string to pure unicode text."""
    tag = re.compile(r"<[^>]*>")
    whites = re.compile(r"[\s]+")
        
    @staticmethod
    def remove(html):
        """Do the conversion HTML -> text"""
        text = unicode(html)
        text = RemoveHTML.tag.sub("", text)
        text = RemoveHTML.whites.sub(" ", text)
        #convert entities
        text = lxml.html.fromstring(text).text
        return text
