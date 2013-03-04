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
Test text processing module.
"""

from __future__ import division
from __future__ import absolute_import              
            
import pytest #contains `skip`, `fail`, `raises`, `config`

import os
import os.path as path
import glob
import time
from datetime import datetime
import re

from numpy import isnan, nan
import pandas as pd
import nltk
from nltk import RegexpTokenizer

import logging
from logging import info
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime



def relative(*path_components):
    "Create file a path that is relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_components))


def make_test_listings():
    """
    Create a DataFrame with some data.
    """
    from clair.coredata import make_listing_frame
    
    fr = make_listing_frame(3)
    #All listings need unique ids
    fr["id"] = ["eb-123", "eb-456", "eb-457"]
    
    fr["training_sample"][0] = True 

    fr["expected_products"][0] = ["nikon-d90", "nikon-sb-24"]
    fr["products"][0] = ["nikon-d90"]
    fr["products_absent"][0] = ["nikon-sb-24"]
    
    fr["title"] = [u"Nikon D90 super duper!", u"<>müäh", None]
    fr["description"][0] = "Buy my old Nikon D90 camera <b>now</b>!"
    fr["prod_spec"][0] = {"Marke":"Nikon", "Modell":"D90"}

    #Put our IDs into index
    fr.set_index("id", drop=False, inplace=True, 
                 verify_integrity=True)
    return fr


def test_HtmlTool_remove_html():
    """Test the HTML to pure text conversion."""
    from clair.textprocessing import HtmlTool
    
    text = HtmlTool.remove_html(
                    "This is <b>bold</b> text.   <p>Paragraph.</p> 3 &gt; 2")
    print text
    assert text == "This is bold text. Paragraph. 3 > 2"
    
    text = HtmlTool.remove_html(
                    """Integrated style sheet. 
                       <style type="text/css"> p {color:blue;} </style>
                       Text after style sheet.""")
    print text
    assert text == "Integrated style sheet. Text after style sheet."
    
    assert HtmlTool.remove_html(None) == ""
    assert HtmlTool.remove_html(nan) == ""
    
    text = HtmlTool.remove_html(" 1 &lt; 2 &gt; 0.5 ")
    print text
    assert text == " 1 < 2 > 0.5 "
   
   
html_nasty = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <title>
            Bedienungsanleitung Nikon SB-26 SB26 SB 26 
            Autofokus-Blitzgerät Anleitung
        </title>
        <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1//TRANSLIT">
    </head>
    <body >
<div id="body_farbe">
<div id="body_kopf">
<div id="body_fuss">
<div id="verpackung">
<div id="content">
<div id="rechts">
<div id="rechts1">
<div id="bild">
<script language="javascript">// 
  function change_picture(thumb, url)
  {
    
    thumb = document.getElementById(thumb);
    bigpic = document.getElementById('bigpicture');
    
    
    bigpic.src = url;
  }
// </script>
</div>
  <!-- Ende bild-->
  <br><br>
</div>
<div id="rechts2">
<div id="text">
    <h1>
        <strong>Bedienungsanleitung</strong> 
        Nikon SB-26 Autofokus-Blitzger&auml;t <strong>Anleitung</strong>
    </h1>
    <p><strong>In deutscher Sprache.</strong></p>
    <p>
        <strong><br><br></strong>In einem guten Zustand, mit leichten 
        altersbedingten Verf&auml;rbungen auf dem Cover und der R&uuml;ckseite.
        <strong><br></strong>
    </p>
</div>
<p><b>Detailierte Produktinformation</b></p>

</div>
<!-- Ende rechts2--></div>
<!-- Ende rechts-->
<!-- Ende verpackung--></div>
<!-- Ende body-fuss--></div>
<!-- Ende body-kopf--></div>
<!-- Ende body-farbe-->
    </body>
</html>
"""

def test_HtmlTool_clean_html():
    """Test HTML cleanup algorithm."""
    from clair.textprocessing import HtmlTool
    
    html_nice = HtmlTool.clean_html("""<head></head>
                                      <body>Foo</body>""")
    print html_nice
    
    html_nice = HtmlTool.clean_html(html_nasty)
#    print html_nasty
    print html_nice
    
    pytest.xfail("LXML does strange things.") #IGNORE:E1101
    assert html_nice.find("Blitzger&auml;t") != -1
    
def test_DataStore():
    """Test the data storage object."""
    from clair.textprocessing import DataStore
    
    d = DataStore()
    
    info("Robust behavior when no data is present. - Must not crash")
    d.read_data(relative("."))
    
    info("")
    info("Must load real data")
    d.read_data(relative("../../example-data"))
    assert len(d.products) > 0
    assert len(d.tasks) > 0
    assert len(d.listings) > 0
    
    
def test_CollectText():
    """Test text collection object"""
    from clair.textprocessing import CollectText
    
    #Convert some test data
    c = CollectText()
    l1 = make_test_listings()
    c.insert_listings(l1)
#    print c.texts
    print c.texts.to_string()
    assert len(c.texts) == 3
    assert set(c.texts.columns) == set(["title", "description", "prod_spec"])
    
    #Process the example listings
    c = CollectText()
    c.insert_listings_from_files(relative("../../example-data"))
    print c.texts
#    print c.texts.to_string()
    assert len(c.texts) >= 100
    assert set(c.texts.columns) == set(["title", "description", "prod_spec"])
    
    lt = c.get_listings_text()
#    print lt
    assert len(lt) == len(c.texts)
    assert isinstance(lt.ix[3], unicode)
    assert  lt.map(lambda u: isinstance(u, unicode)).all()

    tt = c.get_total_text()
#    print tt
    print "len(tt) =", len(tt)
    assert isinstance(tt, unicode) 
    assert len(tt) > 1000
    
    print "finished"


def experiment_update_all_listings():
    """Update all listings."""
    from clair.textprocessing import DataStore
    from clair.network import EbayConnector
    
    print "===================================================================="
    print "                 Updating all listings! "
    print "===================================================================="
    ds = DataStore()
    ec = EbayConnector(relative("../../example-data/python-ebay.apikey"))
    
    ds.read_data(relative("../../example-data")) 
    
    print ds.listings["description"]["eb-150850751507"]
    
    print "Updating", len(ds.listings), "listings..."
#    listings_upd = ec.update_listings(ds.listings)
#    ds.insert_listings(listings_upd)
#    ds.write_listings()
    
    print "finished"


def experiment_CollectText():
    """Experiment with the text collection algorithm."""
    from clair.textprocessing import DataStore, CollectText
    from nltk import FreqDist

    ds = DataStore()
    ct = CollectText()
    
    ds.read_data(relative("../../example-data"))
    ct.insert_listings(ds.listings)
    
    tt = ct.get_total_text()
    print len(tt)
    #tokenization
    #TODO: use: ``nltk.wordpunct_tokenize`` or ``nltk.word_tokenize``???
    #TODO: don't split real numbers "2.8" "3,5" important for lenses.
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
    tokenize_words_pattern = r"""
              \d+(\.\d+)?       # real numbers, e.g. 12.40, 82
            | (\w\.)+           # abbreviations, e.g. z.B., e.g., U.S.A.
            | \w+               # words with optional internal hyphens
           # | [][.,;"'?():-_`]  # these are separate tokens
            """
    tokenize_words = RegexpTokenizer(tokenize_words_pattern, 
                                     gaps=False, discard_empty=True,
                                     flags=re.UNICODE | re.MULTILINE | 
                                           re.DOTALL | re.VERBOSE)
    words = tokenize_words.tokenize(tt.lower())
#    wbounds = re.compile(r"[\s\xa0,.:;!(){}[\]]+")
#    nwhites = re.compile(r"[\s]+")
#    words = wbounds.split(tt.lower())
    print len(words)
    
    unique_words = set(words)
    print len(unique_words)
#    print unique_words
    
    word_freqs = FreqDist(words)
#    word_freqs.plot(200)
    print word_freqs.keys()[:200]
    print word_freqs.keys()[-200:]
    for i, word in enumerate(word_freqs):
        if word_freqs[word] == 1:
            break
        
    print i, "non unique words, first unique word is:", word
    
    word_keys = word_freqs.keys()
    print 'word_freqs["1.4"] =', word_freqs["1.4"], word_keys.index("1.4")
    print 'word_freqs["2.8"] =', word_freqs["2.8"], word_keys.index("2.8")
    print 'word_freqs["3.5"] =', word_freqs["3.5"]  
    print 'word_freqs["5.6"] =', word_freqs["5.6"]
    
#    #Why are there words like "font-size" in the text?
#    search_word = "getelementbyid"
#    listing_texts = ct.get_listings_text()
#    for lid, text in listing_texts.iteritems():
#        i = text.lower().find(search_word)
#        if i != -1:
#            print "Found word:", search_word, "listing ID:", lid, "text position:", i
#            print "Text -------------------------------------"
#            print text
#            print "HTML ---------------------------------------"
#            print ds.listings["description"][lid]
#            break
    
    print "finished"
    
    

if __name__ == "__main__":
#    test_HtmlTool_remove_html()
    test_HtmlTool_clean_html()
#    test_DataStore()
#    test_CollectText()
#    experiment_update_all_listings()
#    experiment_CollectText()
    
    pass #IGNORE:W0107
