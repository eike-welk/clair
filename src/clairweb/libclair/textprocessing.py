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

import re 
# import os.path as path
# import logging
# import random
import html
# import pickle
# 
# import pandas as pd
import numpy as np
# import nltk

# from clair.coredata import Product, DataStore



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
    
    @staticmethod
    def remove_html(in_html):
        """
        Remove tags but keep text, convert entities to Unicode characters.
        """
        if in_html is None:
            return ""
        if isinstance(in_html, float) and np.isnan(in_html):
            return ""
        text = str(in_html)
        text = HtmlTool.script_sheet.sub("", text)
        text = HtmlTool.comment.sub("", text)
        text = HtmlTool.tag.sub("", text)
        text = HtmlTool.nwhites.sub(" ", text)
        text = html.unescape(text)
        return text

    @staticmethod
    def to_nice_text(in_html):
        """Remove all HTML tags, but produce a nicely formatted text."""
        if in_html is None:
            return ""
        if isinstance(in_html, float) and np.isnan(in_html):
            return ""
        text = str(in_html)
        text = HtmlTool.script_sheet.sub("", text)
        text = HtmlTool.comment.sub("", text)
        text = HtmlTool.nwhites.sub(" ", text)
        text = HtmlTool.p_div.sub("\n", text) #convert <p>, <div>, <br> to "\n"
        text = HtmlTool.tag.sub("", text)     #remove all tags
        text = html.unescape(text)
        #Get whitespace right
        text = HtmlTool.nspace.sub(" ", text)
        text = HtmlTool.retspace.sub("\n", text)
        text = HtmlTool.n2ret.sub("\n\n", text)
        text = text.strip()
        return text

    

# class FeatureExtractor(object):
#     """
#     Create feature sets from listings, for the learning algorithms.
#     
#     Also creates list of words that are used in a listing. 
#     """
#     
#     def __init__(self, feature_words=[], use_title=True, use_description=True, #IGNORE:W0102
#                  use_prod_spec=True, use_seller=True):
#         assert all([isinstance(w, str) for w in feature_words])
#         self.feature_words = feature_words
#         self.use_title = use_title
#         self.use_description = use_description
#         self.use_prod_spec = use_prod_spec
#         self.use_seller = use_seller
#     
#     @staticmethod
#     def to_text_dict(in_dict):
#         """Convert dictionary to text. Pattern: 'key: value,'"""
#         if in_dict is None:
#             return ""
#         if isinstance(in_dict, float) and np.isnan(in_dict):
#             return ""
#         
#         text = ""
#         for key, value in in_dict.items():
#             text += str(key) + ": " + str(value) + ", "
#         return text
# 
#     #Split string into words
#     #Alternative tokenizers: ``nltk.wordpunct_tokenize`` or ``nltk.word_tokenize``???
#     #Important: don't split real numbers "2.8" "3,5" important for lenses.
#     #Example for ``nltk.RegexpTokenizer``
#     #>>> text = 'That U.S.A. poster-print costs $12.40...'
#     #>>> pattern = r'''(?x)    # set flag to allow verbose regexps
#     #...     ([A-Z]\.)+        # abbreviations, e.g. U.S.A.
#     #...   | \w+(-\w+)*        # words with optional internal hyphens
#     #...   | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
#     #...   | \.\.\.            # ellipsis
#     #...   | [][.,;"'?():-_`]  # these are separate tokens
#     #... '''
#     #>>> nltk.regexp_tokenize(text, pattern)
#     #['That', 'U.S.A.', 'poster-print', 'costs', '$12.40', '...']
#     word_tokenizer_pattern = r"""
#               \d+(\.\d+)?       # real numbers, e.g. 2.8, 42
#             | \d+(,\d+)?       # German real numbers, e.g. 2,8, 42
#             | (\w\.)+           # abbreviations, e.g., z.B., U.S.A.
#             | \w+               # words
#            # | [][.,;"'?():-_`]  # these are separate tokens
#             """
#     word_tokenizer = RegexpTokenizer(word_tokenizer_pattern, 
#                                       gaps=False, discard_empty=True,
#                                       flags=re.UNICODE | re.MULTILINE | 
#                                             re.DOTALL | re.VERBOSE)
#     
#     def extract_words(self, listing):
#         """Extract words from a listing."""
#         word_tokenizer = FeatureExtractor.word_tokenizer
#         words = []
#         
#         if self.use_title:
#             string = listing["title"]
#             if string:
#                 words += word_tokenizer.tokenize(string.lower())
#         if self.use_description:
#             string = listing["description"]
#             string = HtmlTool.remove_html(string)
#             words += word_tokenizer.tokenize(string.lower())
#         if self.use_prod_spec:
#             string = FeatureExtractor.to_text_dict(listing["prod_spec"])
#             words += word_tokenizer.tokenize(string.lower())
#         if self.use_seller:
#             seller = listing["seller"]
#             if seller:
#                 words += [seller]
#         
#         return words
#     
#     def extract_features(self, listing):
#         """Create the feature dict for a single listing."""
#         listing_words = set(self.extract_words(listing))
#         features = {}
#         for word in self.feature_words:
#             features["contains-" + word] = word in listing_words
#         return features



# class ProductRecognizer(object):
#     """
#     Identify products in a ``DataFrame`` of listings.
#     
#     Together with ``FeatureExtractor`` this class embodies a very 
#     simple text classification algorithm. The text is classified into:
#     *contains product* (``True``) vs. *does not contain product* (``False``).
#     
#     The algorithm is almost exactly as the *Document Classification* 
#     algorithm in:
#     http://nltk.org/book/ch06.in_html#code-document-classify-fd
#     """
#     def __init__(self, product_id, n_features=2000):
#         #ID of product that is identified by this object
#         self.product_id = product_id
#         #size of feature dict
#         self.n_features = n_features
#         self.feature_extractor = FeatureExtractor() #Dummy
#         self.classifier = None
#         
# 
#     def filter_trainig_samples(self, all_listings):
#         """
#         Filter matching training samples from ``DataFrame`` of listings.
#         
#         Returns
#         -------
#         training_samples, n_positive, n_negative : pd.DataFrame, int, int
#         
#         * The training samples for the recognizer's product
#         * the number of (positive) samples that contain the product,
#         * the number of negative samples.
#         """
#         product_id = self.product_id
#         sample_ids, pos_sample_ids, neg_sample_ids = [], [], []
#         for idx, listing in all_listings.iterrows():
# #            print listing.name
#             #Note: three valued logic: 0, 1, nan
#             if listing["training_sample"] != 1.0:
#                 continue
#             products = listing["products"]
#             products_absent = listing["products_absent"]
#             #Discard incomplete or defective training samples
#             if products is None or products_absent is None:
#                 continue
#             if product_id in products:
#                 sample_ids.append(idx)
#                 pos_sample_ids.append(idx)
#             elif product_id in products_absent:
#                 sample_ids.append(idx)
#                 neg_sample_ids.append(idx)
#             
#         training_samples = all_listings.ix[sample_ids]
# #        positive_samples = all_listings.ix[pos_sample_ids]
# #        negative_samples = all_listings.ix[neg_sample_ids]
#         n_positive = len(pos_sample_ids)
#         n_negative = len(neg_sample_ids)
#         return training_samples, n_positive, n_negative
#     
#     
#     def filter_candidate_listings(self, all_listings):
#         """
#         Filter listings that may contain the desired product from 
#         ``DataFrame`` of listings. 
#         
#         The returned listings can then be fed into the product recognition.
#         """
#         product_name = self.product_id
#         
#         def is_candidate(listing):
#             "Determine if product is expected in this listing."
# #            print listing.name            
#             expected_products = listing["expected_products"]
#             if expected_products is None:
#                 return False
#             return (listing["training_sample"] != 1.0 and 
#                     product_name in expected_products)
#             
#         where_sample = all_listings.apply(is_candidate, axis=1)
#         return all_listings.ix[where_sample]
#     
#     
#     def create_labeled_features(self, listings):
#         "Create labeled features to train or check the recognition algorithm."
#         labeled_features = []
#         for product_id, listing in listings.iterrows():
#             features = self.feature_extractor.extract_features(listing)
#             contains_product = self.product_id in listing["products"]
#             if contains_product \
#                == (self.product_id in listing["products_absent"]):
#                 #ignore contradicting information
#                 logging.warn(
#                     "Training sample with contradicting information: {}."
#                     .format(product_id))
#                 continue
#             labeled_features.append((features, contains_product))
#             
#         return labeled_features
#     
#         
#     def train_finder(self, all_listings):
#         """
#         Train the product identification algorithm with example data.
#         """
#         logging.info("Start training of recognizer for product: {0}"
#                      .format(self.product_id))
#         self.classifier = None
#         
#         #select example listings for the finder's product
#         listings, n_pos, n_neg = self.filter_trainig_samples(all_listings)
#         logging.info("Number listings: {l}, positive: {p}, negative: {n}; "
#                      "features: {f}"
#                      .format(l=len(listings), p=n_pos, n=n_neg,
#                              f=self.n_features))
#         if len(listings) < 30:
#             logging.warn("Product {0}. Can't compute classifier. "
#                          "Too few listings."
#                          .format(self.product_id))
#             return
#         elif n_pos < 10:
#             logging.warn("Product {0}. Can't compute classifier. "
#                          "Too few positive listings."
#                          .format(self.product_id))
#             return
#         elif n_neg < 10:
#             logging.warn("Product {0}. Can't compute classifier. "
#                          "Too few negative listings."
#                          .format(self.product_id))
#             return
#         
#         #Create list of most common words, and put it into feature extractor
#         #TODO: remove stop-words
#         self.feature_extractor = FeatureExtractor()
#         word_freqs = FreqDist()
#         for _, listing in listings.iterrows():
#             words = self.feature_extractor.extract_words(listing)
#             word_freqs.update(words)
#         common_words = list(word_freqs.keys())[:self.n_features]
#         self.feature_extractor = FeatureExtractor(common_words)
#         logging.debug("Number individual words: {0}; hapaxes: {1}"
#                       .format(len(word_freqs), len(word_freqs.hapaxes())))
#         logging.debug("Most common words: {}".format(list(word_freqs.keys())[:100]))
#         
#         #Train the classifier
#         train_set = self.create_labeled_features(listings)
#         self.classifier = nltk.NaiveBayesClassifier.train(train_set)
#         self.classifier.show_most_informative_features(20)
#         
#         
#     def compute_accuracy(self, listings):
#         "Test accuracy of classifier."
#         logging.debug("Start testing accuracy of recognizer for product {0};"
#                       "Number listings: {1}"
#                       .format(self.product_id, format(len(listings))))
#         if self.classifier is None:
#             logging.warn("Can't compute recognition accuracy for product {0}. "
#                          "No classifier was trained. "
#                          "Probably too few training samples"
#                          .format(self.product_id))
#             return np.nan
#         
#         listings, _, _ = self.filter_trainig_samples(listings)
#         test_set = self.create_labeled_features(listings)
#         accuracy = nltk.classify.accuracy(self.classifier, test_set)
#         logging.info("Accuracy of recognizer for product {0}: {1}"
#                      .format(self.product_id, accuracy))
#         if accuracy < 0.8:
#             logging.warn("Product {0}. Accuracy is very bad!"
#                          .format(self.product_id)) 
#         return accuracy
#         
#     
#     def contains_product(self, listing):
#         """
#         Recognize the product, for which the recognizer was trained in a 
#         listing.
#         
#         Return
#         ------ 
#         * ``True`` if listing contains the product. 
#         * ``False`` if listing does not contain the product.
#         * ``None`` if recognizer is not correctly trained.
#         """
#         assert isinstance(listing, pd.Series)
#         if self.classifier is None:
# #            logging.warn("Can't recognize product {0}. "
# #                         "No classifier was trained. "
# #                         "Probably too few training samples"
# #                         .format(self.product_id))
#             return None
# 
#         features = self.feature_extractor.extract_features(listing)
#         prod_yn = self.classifier.classify(features)
#         return prod_yn



# class RecognizerController(object):
#     """Coordinate the recognition of products in listings."""
#     def __init__(self):
#         self.recognizers = {}
#         self.data_dir = None
#         self.dirty = False
#         
#     def create_file_name(self, data_dir):
#         "Create file name for storing recognizers on disk."
#         return path.join(data_dir, "product-recognizers.pickle")
#     
#     def read_recognizers(self, data_dir):
#         """
#         Load recognizers from disk. Each product gets a dedicated recognizer.
#         """
#         logging.debug("Loading recognizers from disk...")
#         assert isinstance(data_dir, str)
#         try:        
#             self.data_dir = data_dir
#             file_name = self.create_file_name(data_dir)      
#             pickle_file = open(file_name, "rb")
#             self.recognizers = pickle.load(pickle_file)
#             pickle_file.close()
#             self.dirty = False
#             logging.info("Loaded {} recognizers from disk."
#                          .format(len(self.recognizers)))
#         except IOError as err:
#             logging.error("Loading recognizers from disk failed: {}"
#                           .format(err))
#     
#     def write_recognizers(self, data_dir=None):
#         """Store recognizers on disk"""
#         logging.debug("Writing recognizers to disk...")
#         if data_dir is not None:
#             self.data_dir = data_dir
#         if self.data_dir is None:
#             raise Exception("Unknown data directory. Can't sve file.")
#         try:
#             file_name = self.create_file_name(self.data_dir)
#             pickle_file = open(file_name, "wb")
#             pickle.dump(self.recognizers, pickle_file, protocol=1)
#             pickle_file.close()
#             self.dirty = False
#             logging.info("Wrote {} recognizers to disk."
#                          .format(len(self.recognizers)))
#         except IOError as err:
#             logging.error("Writing recognizers to disk failed: {}"
#                           .format(err))
#     
#     
#     def train_recognizers(self, products, listings, progress_dialog=None):
#         """
#         Create new recognizers and train them. Each product gets a 
#         dedicated recognizer.
#         """
#         assert isinstance(products, list)
#         assert all([isinstance(p, Product) for p in products])
#         assert isinstance(listings, pd.DataFrame)
#         
#         #create and train recognizers if necessary
#         #TODO: check for new training samples, and train only if new training
#         #      samples exist
#         train_listings = listings[listings["training_sample"] == 1.0]
#         for i, product in enumerate(products):
#             finder = ProductRecognizer(product.id)
#             finder.train_finder(train_listings)
#             self.recognizers[product.id] = finder
#             #Drive event loop, and advance progress dialog if it exists
#             if progress_dialog is not None:
#                 progress_dialog.setValue(i * 10)
#                 if progress_dialog.wasCanceled():
#                     break
#         self.dirty = True
#     
#     
#     def recognize_products(self, candidate_ids, all_listings, 
#                            progress_dialog=None):
#         """
#         Iterate over ``candidate_ids`` and identify expected products in 
#         ``all_listings`` with these IDs.
#         """
#         logging.info("Recognizing products in {0} listings."
#                      .format(len(candidate_ids)))
#         
#         n_train, n_regular = 0, 0
#         for i, prod_id in enumerate(candidate_ids):
#                 
#             listing = all_listings.ix[prod_id]
#             logging.debug("{}, '{}'".format(prod_id, listing["title"]))
#             
#             #Don't classify training samples
#             if listing["training_sample"] == 1.0:
#                 n_train += 1
#                 logging.debug("-" * 18 + "Training sample.")
#                 continue
#             
#             n_regular += 1 
#             products, products_absent = [], []
#             #Try to identify all expected products
#             for product_id in listing["expected_products"]:
#                 try:
#                     recognizer = self.recognizers[product_id]
#                     contains_product = recognizer.contains_product(listing)
#                     #`contains_product` can be `None`, if recognizer doesn't work
#                     if contains_product == True:
#                         logging.debug(" " * 18 + "contains: {}".
#                                       format(product_id))
#                         products.append(product_id)
#                     elif contains_product == False:
#                         products_absent.append(product_id)
#                 except KeyError:
#                     pass
#                 #Drive event loop, and advance progress dialog if it exists
#                 if progress_dialog is not None:
#                     progress_dialog.setValue(i)
#                     if progress_dialog.wasCanceled():
#                         return
#             
#             #store recognition results in original data frame
#             all_listings["training_sample"][prod_id] = 0.0
#             all_listings["products"][prod_id] = products
#             all_listings["products_absent"][prod_id] = products_absent
#         
#         logging.debug("Classified {0} listings, ignored {1} training samples."
#                       .format(n_regular, n_train))



# def split_random(data_frame, fraction):
#     """
#     Split ``DataFrame`` row-wise and randomly into two parts.
#     
#     Parameters
#     ----------
#     
#     data_frame : ``pd.DataFrame``
#         Container for rows that are randomly distributed into two parts.
#         
#     fraction : float
#         Must be in range 0..1. Fraction of the rows that are placed
#         in the first part of the result.
#         
#     Returns
#     --------
#     ``pd.DataFrame, pd.DataFrame``
#         The two parts into which ``data_frame`` is split.
#     """
#     assert 0.0 <= fraction <= 1.0
#     
#     #Always generate the indexes of the smaller fraction
#     swap_fractions = False
#     if fraction > 0.5:
#         fraction = 1 - fraction
#         swap_fractions = True
#         
#     #Create set of indexes that will be in the first (smaller) fraction
#     element_idxs = set()
#     len_data = len(data_frame)
#     n_idx_wanted = int(round(len_data * fraction))
#     # TODO: Use random choice library function
#     for _ in range(n_idx_wanted):
#         idx = int(random.random() * len_data)
#         element_idxs.add(idx)
#     while len(element_idxs) < n_idx_wanted:
#         idx = int(random.random() * len_data)
#         element_idxs.add(idx)
#         
#     #Create series with `True` for each row in 1st fraction.
#     fancy_idx = np.zeros((len_data,), dtype=bool)
#     for idx in element_idxs:
#         fancy_idx[idx] = True
#     
#     #Split the data frame's rows in two fractions
#     frac1 = data_frame[fancy_idx]
#     frac2 = data_frame[~fancy_idx]
#     if swap_fractions:
#         frac1, frac2 = frac2, frac1
#         
#     return frac1, frac2
