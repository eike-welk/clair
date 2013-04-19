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
import logging
import random
import HTMLParser

#import lxml.html
import lxml.html.clean
import pandas as pd
from numpy import isnan
import nltk
from nltk import RegexpTokenizer

from clair.coredata import DataStore



class HtmlTool(object):
    """
    Algorithms to process HTML.
    
    TODO: Look at html2text which converts HTML to markdown
          https://github.com/aaronsw/html2text/blob/master/html2text.py
    """
    #Regular expressions to recognize different parts of HTML. 
    #Internal style sheets or JavaScript 
    script_sheet = re.compile(r"<(script|style).*?>.*?(</\1>)", 
                              re.IGNORECASE | re.DOTALL)
    #HTML comments - can contain ">"
    comment = re.compile(r"<!--(.*?)-->", re.DOTALL) 
    #HTML tags: <any-text>
    tag = re.compile(r"<.*?>", re.DOTALL)
    #Consecutive whitespace characters
    nwhites = re.compile(r"[\s]+")
    #<p>, <div>, <br> tags and associated closing tags
    p_div = re.compile(r"</?(p|div|br).*?>", 
                       re.IGNORECASE | re.DOTALL)
    #Consecutive whitespace, but no newlines
    nspace = re.compile("[^\S\n]+", re.UNICODE)
    #At least two consecutive newlines
    n2ret = re.compile("\n\n+")
    #A return followed by a space
    retspace = re.compile("(\n )")
    
    #For converting HTML entities to unicode
    html_parser = HTMLParser.HTMLParser()
    #Remove unwanted tags
    cleaner = lxml.html.clean.Cleaner(remove_unknown_tags=True,
                                      page_structure=False,
                                      style=True,
                                      remove_tags=["div", "a", "img"])
    
    @staticmethod
    def remove_html(html):
        """
        Remove tags but keep text, convert entities to Unicode characters.
        """
        if html is None:
            return u""
        if isinstance(html, float) and isnan(html):
            return u""
        text = HtmlTool.script_sheet.sub("", html)
        text = HtmlTool.comment.sub("", text)
        text = HtmlTool.tag.sub("", text)
        text = HtmlTool.nwhites.sub(" ", text)
        text = HtmlTool.html_parser.unescape(text)
        text = unicode(text)
        return text

    @staticmethod
    def to_nice_text(html):
        """Remove all HTML tags, but produce a nicely formatted text."""
        if html is None:
            return u""
        if isinstance(html, float) and isnan(html):
            return u""
        text = unicode(html)
        text = HtmlTool.script_sheet.sub("", text)
        text = HtmlTool.comment.sub("", text)
        text = HtmlTool.nwhites.sub(" ", text)
        text = HtmlTool.p_div.sub("\n", text) #convert <p>, <div>, <br> to "\n"
        text = HtmlTool.tag.sub("", text)     #remove all tags
        text = HtmlTool.html_parser.unescape(text)
        #Get whitespace right
        text = HtmlTool.nspace.sub(" ", text)
        text = HtmlTool.retspace.sub("\n", text)
        text = HtmlTool.n2ret.sub("\n\n", text)
        text = text.strip()
        return text
    
    @staticmethod
    def clean_html(html):
        """
        Beautify html, remove any messy or unsafe tags.
        TODO: Fix this method, it has problems with umlauts, and produces ugly html.
        """
        return HtmlTool.cleaner.clean_html(html)
    
    

class Tokenizer(object):
    """Create tokens for the learning algorithms."""
    
    def __init__(self, use_title=True, use_description=True, 
                 use_prod_spec=True, use_seller=True):
        self.use_title = use_title
        self.use_description = use_description
        self.use_prod_spec = use_prod_spec
        self.use_seller = use_seller
    
    @staticmethod
    def to_text_dict(in_dict):
        """Convert dictionary to text. Pattern: 'key: value,'"""
        if in_dict is None:
            return u""
        if isinstance(in_dict, float) and isnan(in_dict):
            return u""
        
        text = ""
        for key, value in in_dict.iteritems():
            text += unicode(key) + ": " + unicode(value) + ", "
        return text

    #Split string into words
    #Alternative tokenizers: ``nltk.wordpunct_tokenize`` or ``nltk.word_tokenize``???
    #Important: don't split real numbers "2.8" "3,5" important for lenses.
    #Example for ``nltk.RegexpTokenizer``
    #>>> text = 'That U.S.A. poster-print costs $12.40...'
    #>>> pattern = r'''(?x)    # set flag to allow verbose regexps
    #...     ([A-Z]\.)+        # abbreviations, e.g. U.S.A.
    #...   | \w+(-\w+)*        # words with optional internal hyphens
    #...   | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
    #...   | \.\.\.            # ellipsis
    #...   | [][.,;"'?():-_`]  # these are separate tokens
    #... '''
    #>>> nltk.regexp_tokenize(text, pattern)
    #['That', 'U.S.A.', 'poster-print', 'costs', '$12.40', '...']
    word_tokenizer_pattern = r"""
              \d+(\.\d+)?       # real numbers, e.g. 2.8, 82
            | (\w\.)+           # abbreviations, e.g., z.B., U.S.A.
            | \w+               # words
           # | [][.,;"'?():-_`]  # these are separate tokens
            """
    word_tokenizer = RegexpTokenizer(word_tokenizer_pattern, 
                                      gaps=False, discard_empty=True,
                                      flags=re.UNICODE | re.MULTILINE | 
                                            re.DOTALL | re.VERBOSE)
    
    def extract_words(self, listing):
        """Extract words from a listing."""
        word_tokenizer = Tokenizer.word_tokenizer
        words = []
        
        if self.use_title:
            string = listing["title"]
            if string:
                words += word_tokenizer.tokenize(string.lower())
        if self.use_description:
            string = listing["description"]
            if string:
                words += word_tokenizer.tokenize(string.lower())
        if self.use_prod_spec:
            string = Tokenizer.to_text_dict(listing["prod_spec"])
            words += word_tokenizer.tokenize(string.lower())
        if self.use_seller:
            words += [listing["seller"]]
            
        return words
    
    def extract_features(self, listing):
        """Create the feature dict for a single listing."""
        words = self.extract_words(listing)
        features = {"contains_" + word: True for word in words}
        return features
    


def split_random(data_frame, fraction):
    """Split rows of ``DataFrame`` randomly into two parts."""
    assert 0.0 <= fraction <= 1.0
    
    #Always generate the indexes of the smaller fraction
    swap_fractions = False
    if fraction > 0.5:
        fraction = 1 - fraction
        swap_fractions = True
        
    #Create set of indexes that will be in the first (smaller) fraction
    element_idxs = set()
    len_data = len(data_frame)
    n_idx_wanted = int(round(len_data * fraction))
    for _ in xrange(n_idx_wanted):
        idx = int(random.random() * len_data)
        element_idxs.add(idx)
    while len(element_idxs) < n_idx_wanted:
        idx = int(random.random() * len_data)
        element_idxs.add(idx)
        
    #Create series with `True` for each row in fraction-1
    fancy_idx = pd.Series(False, index=range(len_data))
    for idx in element_idxs:
        fancy_idx[idx] = True
    
    #Split the data frame's rows in two fractions
    frac1 = data_frame[fancy_idx]
    frac2 = data_frame[~fancy_idx]
    if swap_fractions:
        frac1, frac2 = frac2, frac1
        
    return frac1, frac2
        
    
    
class CollectText(object):
    """Extract text from listings"""
    def __init__(self):
        self.texts = pd.DataFrame()
        
        
    @staticmethod
    def to_text_dict(in_dict):
        """Convert dictionary to text. Pattern: 'key: value,'"""
        if in_dict is None:
            return u""
        if isinstance(in_dict, float) and isnan(in_dict):
            return u""
        
        text = ""
        for key, value in in_dict.iteritems():
            text += unicode(key) + ": " + unicode(value) + ", "
        return text
    
        
    def merge_listings(self, listings):
        """Extract the text from listings and store it in ``self.text``"""
        text_title = listings["title"].map(HtmlTool.remove_html)
        text_desctription = listings["description"].map(HtmlTool.remove_html)
        text_specs = listings["prod_spec"].map(self.to_text_dict)
        
        texts = pd.DataFrame(index=listings.index)
        texts["title"] = text_title
        texts["description"] = text_desctription
        texts["prod_spec"] = text_specs
        #TODO: insert also "*products*" and "training_sample"
        self.texts = texts.combine_first(self.texts)
        

    def insert_listings_from_files(self, data_dir):
        """Get listings from disk, and extract their text contents."""
        data = DataStore()
        data.read_data(data_dir)
        self.merge_listings(data.listings)
        
    def get_listings_text(self):
        """Return text for each listing separate, as Series."""
        return self.texts["title"] + self.texts["description"] + \
               self.texts["prod_spec"]

    def get_total_text(self):
        """Get text of all listings as single string"""
        return self.get_listings_text().sum()

