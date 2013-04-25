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
   
   
html_nasty = u"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
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

def test_HtmlTool_to_nice_text():
    """Test HTML cleanup algorithm."""
    from clair.textprocessing import HtmlTool
    
    text_nice = HtmlTool.to_nice_text(html_nasty)
    print html_nasty
    print text_nice
    
    assert text_nice.find(u"Blitzgerät") != -1
    assert text_nice.find(u"Rückseite") != -1
    assert len(text_nice.split("\n")) == 8
    
    
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
    
    
def test_FeatureExtractor():
    """Test ``FeatureExtractor`` class."""
    from clair.textprocessing import FeatureExtractor
    from clair.coredata import DataStore
    
    data_dir = relative("../../example-data")
    data = DataStore()
    data.read_data(data_dir)
    listing = data.listings.ix["eb-110685959294"]
    
    #Words to test different extraction functionality
    #                from title and description, test entities
    feature_words = ["nikon", "photo", "d90", u"blitzgerät",
    #                seller, item specifics
                     "photo-porst-memmingen", "mpn",
    #                words that are not in listing
                     "foo", "bar"]
    
    extractor = FeatureExtractor(feature_words)
    features = extractor.extract_features(listing)
    
    print features
    
    assert features['contains-photo'] == True
    assert features['contains-photo-porst-memmingen'] == True
    assert features['contains-nikon'] == True
    assert features['contains-mpn'] == True
    assert features['contains-d90'] == True
    assert features[u'contains-blitzgerät'] == True
    
    assert features['contains-foo'] == False
    assert features['contains-bar'] == False
    
    print "finished"
    
    
def test_ProductRecognizer():
    """Test ``FeatureExtractor`` class."""
    from clair.textprocessing import ProductRecognizer, split_random
    from clair.coredata import DataStore
    
    data_dir = relative("../../example-data")
    data = DataStore()
    data.read_data(data_dir)
    
    finder = ProductRecognizer("nikon-d70")
    
    print "Test: filter_trainig_samples"
    samples = train_samples = finder.filter_trainig_samples(data.listings)
    print "Number training samples:", len(samples)
#    print samples
    assert len(samples) > 100
    assert all(samples["training_sample"] == True)
    pe = samples["products"].map(lambda l: "nikon-d70" in l)
    pa = samples["products_absent"].map(lambda l: "nikon-d70" in l)
    assert all(pe | pa)
        
    print "\nTest: filter_candidate_listings"
    samples = cand_samples = finder.filter_candidate_listings(data.listings)
    print "Number candidate samples:", len(samples)
    assert len(samples) > 10
    assert all(samples["training_sample"] != 1.0)
    pe = samples["expected_products"].map(lambda l: "nikon-d70" in l)
    assert all(pe)
    
    print "\nTest: train_finder, compute_accuracy"
    train_set, test_set = split_random(train_samples, 0.8)
    finder.train_finder(train_set)
    finder.compute_accuracy(test_set)
    
    print "\nTest: contains_product"
    for i, (_, listing) in enumerate(cand_samples.iterrows()):
        if i >= 10:
            break
        contains = finder.contains_product(listing)
        print listing["title"]
        print "Contains", finder.product_id, ":", contains
        print 
    
    print "finished"
    
    
def test_RecognizerController():
    """Test ``RecognizerController`` class."""
    from clair.textprocessing import RecognizerController
    from clair.coredata import DataStore
    
    data_dir = relative("../../example-data")
    data = DataStore()
    data.read_data(data_dir)
    
    controller = RecognizerController()
    #create new recognizers and train them
    controller.train_recognizers(data.products, data.listings)
    #Save and load the newly created recognizers to/from disk. 
    controller.write_recognizers(data_dir)
    controller = RecognizerController()
    controller.read_recognizers(data_dir)
    #Save recognizers to disk use internal file name. 
    controller.write_recognizers()
    #Iterate over all listings and recognize products
    controller.recognize_products(data.listings.index, data.listings)
    
    #TODO: assertions
#    data.write_listings()
    
    print "finished"

    
def test_split_random():
    """Test splitting frame into two fractions randomly."""
    from clair.textprocessing import split_random
    
    df = pd.DataFrame({"aaa":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
#    print df
    
    frac1, frac2 = split_random(df, 0.3)
#    print frac1
#    print frac2
    assert len(frac1) == 3 and len(frac2) == 7
    
    frac1, frac2 = split_random(df, 0.8)
#    print frac1
#    print frac2
    assert len(frac1) == 8 and len(frac2) == 2
    
    #Simple test for randomness
    print split_random(df, 0.4)[0].index
    assert any(split_random(df, 0.4)[0].index != split_random(df, 0.4)[0].index)
    
    print "finished"
    
    
def experiment_update_all_listings():
    """Update all listings."""
    from clair.coredata import DataStore
    from clair.network import EbayConnector
    
    print "===================================================================="
    print "                 Updating all listings! "
    print "===================================================================="
    ds = DataStore()
    ec = EbayConnector(relative("../../example-data/python-ebay.apikey"))
    
    ds.read_data(relative("../../example-data")) 
    
#    print ds.listings["description"]["eb-150850751507"]
    
    print "Updating", len(ds.listings), "listings..."
    listings_upd = ec.update_listings(ds.listings)
    ds.merge_listings(listings_upd)
    ds.write_listings()
    
    print "finished"    
    


if __name__ == "__main__":
#    test_HtmlTool_remove_html()
#    test_HtmlTool_to_nice_text()
#    test_HtmlTool_clean_html()
#    test_FeatureExtractor()
#    test_ProductRecognizer()
    test_RecognizerController()
#    test_split_random()
#    experiment_update_all_listings()
    
    pass #IGNORE:W0107
