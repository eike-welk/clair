# -*- coding: utf-8 -*-
###############################################################################
#    Clair - Project to discover prices on e-commerce sites.                  #
#                                                                             #
#    Copyright (C) 2016 by Eike Welk                                          #
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
Input and Output of data in JSON format.
"""

from __future__ import division
from __future__ import absolute_import              

import os
import os.path as path
import glob
#import string
from datetime import datetime #, timedelta
from types import NoneType
import random
import logging

import dateutil
from numpy import nan, isnan #IGNORE:E0611
import pandas as pd
from lxml import etree, objectify

from clair.descriptors import TableDescriptor


#Structure of DataFrame -> JSON conversion:
#-----------------------------------------------

#Split DataFrame into fragments that are saved separately

#Test if given DataFrame conforms to descriptor
#Convert descriptor to dict
#Convert DataFrame to dict
#Assemble complete dict that contains DataFrame and header
#Convert dict to JSON and write it to a temporary file
#Rename the temporary file.
#    Renaming temporary files is done by a separate object that can be reused

class JsonWriter(object):
    """
    Convert DataFrame objects to JSON, and write them to disk.
    """
    def __init__(self, descriptor):
        assert isinstance(descriptor, TableDescriptor)
        self.descriptor = descriptor
        
    def convert_to_dict(self, frame):
        assert isinstance(frame, pd.DataFrame)
        #TODO: Remove columns that are not in descriptor.
        #TODO: convert dates and times
        frame_dict = frame.to_dict(orient='records')
        out_dict = {'name': self.descriptor.name, 
                    'version': self.descriptor.version,
                    'comment': self.descriptor.comment,
                    'data': frame_dict}
        return out_dict
        

#Loading and saving series of files
#--------------------------------------------------

#Loading and saving series of files is a top level process
#Can be used with different writer and reader objects.


    
#class XMLConverter(object):
#    """
#    Base class for objects that convert to and from XML
#    
#    Unicode introduction
#    http://docs.python.org/2/howto/unicode.html
#    
#    https://github.com/dmw/pyxser
#    http://pyxml.sourceforge.net/topics/howto/node26.html
#    """
#    E = objectify.ElementMaker(
#            annotate=False, 
#            nsmap={"xsi":"http://www.w3.org/2001/XMLSchema-instance"})
#
#    def to_xml_list(self, tag, el_list):
#        """Convert lists, wrap each element of a list with a tag."""
#        if el_list is None:
#            return [None]
#        if isinstance(el_list, float) and isnan(el_list):
#            return [None]
#        E = self.E
#        node = getattr(E, tag)
#        xml_nodes = [node(el) for el in el_list]
#        return xml_nodes
#    
#    
#    def from_xml_list(self, tag, xml_list):
#        """Convert a repetition of XML elements into a Python list."""
#        ustrn = self.unicode_or_none
#        if isinstance(xml_list, objectify.NoneElement):
#            return None
#        
#        try:
#            elements = getattr(xml_list, tag)
#        except AttributeError:
#            return []
#        
#        el_list = []
#        for el in elements:
#            #TODO: convert structured elements.
#            el_list.append(ustrn(el.pyval))
#        return el_list
#    
#    
#    def to_xml_dict(self, py_dict):
#        """Convert a dict to a XML structure"""
#        if py_dict is None:
#            return [None]
#        if isinstance(py_dict, float) and isnan(py_dict):
#            return [None]
#        E = self.E
#        xml_dict_repr = [E.kv_pair(E.key(k), E.value(v)) 
#                         for k, v in py_dict.iteritems()]
#        return xml_dict_repr
#    
#    
#    def from_xml_dict(self, xml_dict):
#        """Convert a special XML structure to a dict."""
#        ustrn = self.unicode_or_none
#        if isinstance(xml_dict, objectify.NoneElement):
#            return None
#        
#        try:
#            xml_kv_pairs = xml_dict.kv_pair
#        except AttributeError:
#            return {}
#        
#        py_dict = {}
#        for xml_kv_pair in xml_kv_pairs:
#            key = ustrn(xml_kv_pair.key.pyval)
#            value = ustrn(xml_kv_pair.value.pyval)
#            py_dict[key] = value
#            
#        return py_dict
#    
#    
#    def unicode_or_none(self, value):
#        """
#        Convert value to a unicode string, but if value is None return None.
#        """
#        if value is None:
#            return None
#        else:
#            return unicode(value)
#
#
#    def datetime_or_none(self, str_none):
#        """
#        Convert ``str_none`` to ``datetime``, but if it is None return None.
#        """
#        if str_none is None:
#            return None
#        else:
#            return dateutil.parser.parse(str_none)
#        
#        
#    def float_or_none(self, float_none):
#        """
#        Convert ``float_none`` to ``float``, but if it is None return None.
#        """
#        if float_none is None:
#            return None
#        else:
#            return float(float_none)
#        
#        
#    def int_or_none(self, int_none):
#        """
#        Convert ``int_none`` to ``int``, but if it is None return None.
#        """
#        if int_none is None:
#            return None
#        else:
#            return int(int_none)
#        
#        
#
#class XMLConverterListings(XMLConverter):
#    """
#    Convert listings to and from XML
#    
#    TODO: XML escapes for description
#    http://wiki.python.org/moin/EscapingXml
#    """
#    def to_xml(self, listings):
#        """Convert DataFrame with listings/auctions to XML."""
#        E = self.E
#
#        root_xml = E.listing_storage(
#            E.version("0.1"),
#            E.listings())
#        for i in range(len(listings.index)):
#            li = listings.ix[i]
#            li_xml = E.listing(
#                E.id(li["id"]),
#                E.training_sample(float(li["training_sample"])),
#                E.search_tasks(*self.to_xml_list("task", li["search_tasks"])),
#                E.expected_products(*self.to_xml_list(
#                                        "product", li["expected_products"])),
#                E.products(*self.to_xml_list("product", li["products"])),
#                E.products_absent(*self.to_xml_list(
#                                        "product", li["products_absent"])),
#                E.thumbnail(li["thumbnail"]),
#                E.image(li["image"]),
#                E.title(li["title"]),
#                E.description(li["description"]),
#                E.prod_spec(*self.to_xml_dict(li["prod_spec"])),
#                E.active(float(li["active"])),
#                E.sold(float(li["sold"])),
#                E.currency(li["currency"]),
#                E.price(float(li["price"])),
#                E.shipping(float(li["shipping"])),
#                E.type(li["type"]),
#                E.time(li["time"]),
#                E.location(li["location"]),
#                E.postcode(li["postcode"]),
#                E.country(li["country"]),
#                E.condition(float(li["condition"])),
#                E.seller(li["seller"]),
#                E.buyer(li["buyer"]),
#                E.server(li["server"]),
#                E.server_id(li["server_id"]),
#                E.final_price(float(li["final_price"])),
#                E.url_webui(li["url_webui"]) )
#            root_xml.listings.append(li_xml)
#        
##        doc_xml = etree.ElementTree(root_xml)
#        doc_str = etree.tostring(root_xml, pretty_print=True)
#        return doc_str 
#        
#        
#    def from_xml(self, xml):
#        """Convert XML string into DataFrame with listings/auctions"""
#        ustr = self.unicode_or_none
#        parse_date = self.datetime_or_none
#        
#        root_xml = objectify.fromstring(xml)
##        print objectify.dump(root_xml)
#        version = root_xml.version.text
#        assert version == "0.1"
#        
#        try: listing_xml = root_xml.listings.listing
#        except AttributeError: return make_listing_frame(0)
#        nrows = len(listing_xml)
#        listings = make_listing_frame(nrows)
#        for i, li in enumerate(listing_xml):    
#            listings.ix[i, "id"] = ustr(li.id.pyval) 
#            listings.ix[i, "training_sample"] = li.training_sample.pyval
#            try: listings.ix[i, "search_tasks"] = [ustr(li.search_task.pyval)] #TODO: remove after 2013-04-30
#            except AttributeError: pass
#            try: listings.set_value(i, "search_tasks", 
#                                    self.from_xml_list("task", li.search_tasks))
#            except AttributeError: pass
#            listings.set_value(i, "expected_products", 
#                               self.from_xml_list("product", li.expected_products))
#            listings.set_value(i, "products", 
#                               self.from_xml_list("product", li.products))
#            try: listings.set_value(i, "products_absent", 
#                                    self.from_xml_list("product", li.products_absent))
#            except AttributeError: pass
#            listings.ix[i, "thumbnail"] = ustr(li.thumbnail.pyval)
#            listings.ix[i, "image"] = ustr(li.image.pyval)
#            listings.ix[i, "title"] = ustr(li.title.pyval )
#            listings.ix[i, "description"] = ustr(li.description.pyval)
#            listings.set_value(i, "prod_spec", self.from_xml_dict(li.prod_spec))
#            listings.ix[i, "active"] = li.active.pyval
#            listings.ix[i, "sold"] = li.sold.pyval
#            listings.ix[i, "currency"] = ustr(li.currency.pyval)
#            listings.ix[i, "price"]    = li.price.pyval
#            listings.ix[i, "shipping"] = li.shipping.pyval
#            listings.ix[i, "type"] = ustr(li.type.pyval)
#            listings.ix[i, "time"] = parse_date(li.time.pyval)
#            listings.ix[i, "location"] = ustr(li.location.pyval)
#            listings.ix[i, "postcode"] = ustr(li.postcode.pyval)
#            listings.ix[i, "country"] = ustr(li.country.pyval)
#            listings.ix[i, "condition"] = li.condition.pyval
#            try: listings.ix[i, "seller"] = ustr(li.seller.pyval)
#            except AttributeError: pass
#            try: listings.ix[i, "buyer"] = ustr(li.buyer.pyval)
#            except AttributeError: pass
#            listings.ix[i, "server"] = ustr(li.server.pyval)
#            listings.ix[i, "server_id"] = ustr(li.server_id.pyval) #ID of listing on server
#            listings.ix[i, "final_price"] = li.final_price.pyval
##            listings["data_directory"] = ""
#            listings.ix[i, "url_webui"] = ustr(li.url_webui.pyval)
##            listings["server_repr"][i] = nan
#
#        #Put our IDs into index
#        listings.set_index("id", drop=False, inplace=True, 
#                           verify_integrity=True)
#        return listings
#
#
#
#class XMLConverterProducts(XMLConverter):
#    """Convert a list of Product objects to and from XML"""
#    def to_xml(self, product_list):
#        """Convert dictionary of Product to XML"""
#        E = self.E
#
#        root_xml = E.product_storage(
#            E.version("0.1"),
#            E.products())
#        for pr in product_list:
#            pr_xml = E.product(
#                E.id(pr.id),
#                E.name(pr.name),
#                E.description(pr.description),
#                E.important_words(*self.to_xml_list("word", 
#                                                    pr.important_words)),
#                E.categories(*self.to_xml_list("category", pr.categories)),
#                )
#            root_xml.products.append(pr_xml)
#        
#        doc_str = etree.tostring(root_xml, pretty_print=True)
#        return doc_str 
#
#        
#    def from_xml(self, xml):
#        """Convert from XML representation to list of Product."""
#        root_xml = objectify.fromstring(xml)
##        print objectify.dump(root_xml)
#        version = root_xml.version.text
#        assert version == "0.1"
#        
#        try: product_xml = root_xml.products.product
#        except AttributeError: return []
#        product_list = []
#        for pr in product_xml:    
#            prod = Product(id=pr.id.pyval,
#                           name=pr.name.pyval,
#                           description=pr.description.pyval,
#                           important_words=self.from_xml_list(
#                                                "word", pr.important_words),
#                           categories=self.from_xml_list(
#                                                "category", pr.categories))
#            product_list.append(prod)
#        
#        return product_list
#
#
#
#class XMLConverterTasks(XMLConverter):
#    """
#    Convert list of task objects to and from XML
#    
#    Currently only stores SearchTask objects.
#    """
#    def to_xml(self, task_list):
#        """Convert dictionary or list of tasks to XML"""
#        E = self.E
#
#        root_xml = E.task_storage(
#            E.version("0.1"),
#            E.tasks())
#        for tsk in task_list:
#            if not isinstance(tsk, SearchTask):
#                continue
#            tsk_xml = E.search_task(
#                E.id(tsk.id),
#                E.due_time(tsk.due_time),
#                E.server(tsk.server),
#                E.recurrence_pattern(tsk.recurrence_pattern),
#                E.query_string(tsk.query_string),
#                E.n_listings(tsk.n_listings),
#                E.price_min(tsk.price_min),
#                E.price_max(tsk.price_max),
#                E.currency(tsk.currency),
#                E.expected_products(*self.to_xml_list("product", 
#                                                      tsk.expected_products))
#                )
#            root_xml.tasks.append(tsk_xml)
#        
#        xml_str = etree.tostring(root_xml, pretty_print=True)
#        return xml_str 
#
#        
#    def from_xml(self, xml):
#        """Convert from XML representation to list of Product."""
#        ustrn = self.unicode_or_none
#        parse_date = self.datetime_or_none
#        floatn = self.float_or_none
#        intn = self.int_or_none
#        
#        root_xml = objectify.fromstring(xml)
##        print objectify.dump(root_xml)
#        version = root_xml.version.text
#        assert version == "0.1"
#               
#        try: task_xml = root_xml.tasks.search_task
#        except AttributeError: return []
#        task_list = []
#        for tsk in task_xml:    
#            prod = SearchTask(id=tsk.id.pyval,
#                              due_time=parse_date(tsk.due_time.pyval), 
#                              server=ustrn(tsk.server.pyval), 
#                              recurrence_pattern=ustrn(
#                                                tsk.recurrence_pattern.pyval), 
#                              query_string=ustrn(tsk.query_string.pyval), 
#                              n_listings=intn(tsk.n_listings.pyval), 
#                              price_min=floatn(tsk.price_min.pyval), 
#                              price_max=floatn(tsk.price_max.pyval), 
#                              currency=ustrn(tsk.currency.pyval), 
#                              expected_products=self.from_xml_list(
#                                        "product", tsk.expected_products)
#                              )
#            task_list.append(prod)
#        
#        return task_list
#
#
#
##Earliest and latest possible date for ``datetime``
#EARLIEST_DATE = datetime(1, 1, 1)
#LATEST_DATE = datetime(9999, 12, 31) 
#
#class XmlIOBigFrame(object):
#    """
#    Store big DataFrame objects as XML files.
#    
#    Assumes that the DataFrame has "time" and "id" columns. The data is split
#    into chunks, that are stored in separate files. Each chunk contains the 
#    data of one month. IDs must be unique. If there are multiple rows with 
#    the same ID, only the last row is kept.
#    
#    Constructor Parameters
#    ----------------------
#    
#    name_prefix : str
#        String that is prepended to all file names.
#        
#    directory : str
#        Directory into which all files are written.
#        
#    xml_converter : object
#        Converts DataFrame to and from XML. Must have methods:
#        ``to_xml`` and ``from_xml``. 
#    """
#    def __init__(self, directory, name_prefix, xml_converter):
#        assert isinstance(name_prefix, basestring)
#        assert isinstance(directory, basestring)
#        if xml_converter is not None:
#            assert hasattr(xml_converter, "to_xml")
#            assert hasattr(xml_converter, "from_xml")
#        
#        self.name_prefix = name_prefix
#        self.directory = directory
#        self.xml_converter = xml_converter
#        
#    
#    def normalize_date(self, date):
#        """Set all fields of ``date`` to 0 except ``year`` and ``month``."""
#        return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#    
#    
#    def make_filename(self, date, number, compress):
#        """
#        Create a filename or glob pattern
#        """
#        date_str = date.strftime("%Y-%m-01") if date is not None else "*"
#        #http://docs.python.org/2/library/string.html#formatstrings
#        num_str = "{:0>3d}".format(number) if number is not None else "*"
#        if compress == True:
#            ext_str = "xmlzip"
#        elif compress == False:
#            ext_str = "xml"
#        else:
#            ext_str = "*"
#            
#        filename = "{pref}.{date}.{num}.{ext}".format(pref=self.name_prefix,
#                                                      date=date_str,
#                                                      num=num_str,
#                                                      ext=ext_str)
#        return filename
#        
#        
#    def write_text(self, text, date, compress, overwrite):
#        """
#        Write text file to disk.
#        
#        Parameter
#        ----------
#        
#        text : str, unicode
#            Contents of file
#            
#        date : datetime
#            Used as part of file name 
#            
#        compress : bool
#            Compress the file's contents.
#        
#        overwrite : bool
#            Don't overwrite existing file, but create additional file with
#            increased serial number in file name.
#        
#        #TODO: compression
#        """
#        assert isinstance(text, basestring)
#        assert isinstance(date, datetime)
#        assert isinstance(compress, bool)
#        assert isinstance(overwrite, bool)
#        
#        if overwrite:
#            self._write_text_overwrite(text, date, compress)
#        else:
#            self._write_text_new_file(text, date, compress)
#        
#    
#    def _write_text_overwrite(self, text, date, compress):
#        """
#        Write text file to disk.
#        
#        Overwrite existing file, delete all other files with same prefix
#        and date in file name.
#
#        #TODO: compression
#        """
#        rand_str = str(random.getrandbits(32))
#        #Get existing file for specified month, create temporary names for them
#        file_pattern = path.join(self.directory, 
#                                 self.make_filename(date, None, None))
#        files_old = glob.glob(file_pattern)
#        files_old_temp = [f + "-old-" + rand_str for f in files_old]
#        #make file name(s) for new file
#        file_new = path.join(self.directory,
#                             self.make_filename(date, 0, compress))
#        file_new_temp = file_new + "-new-" + rand_str
#        
#        #Write file with temporary name
#        if compress:
#            raise IOError("Compression is not implemented.")
#        logging.debug("Writing: {}".format(file_new_temp))
#        fw = open(file_new_temp, "w")
#        fw.write(text.encode("ascii"))
#        fw.close()
#        
#        #Rename old files 
#        for f_old, f_temp in zip(files_old, files_old_temp):
#            os.rename(f_old, f_temp)
#        #Rename new file to final name
#        os.rename(file_new_temp, file_new)
#        #Delete old files
#        for f_temp in files_old_temp:
#            os.remove(f_temp)
#    
#    
#    def _write_text_new_file(self, text, date, compress):
#        """
#        Write text file to disk.
#        
#        Doesn't overwrite existing file, but create additional file with
#        increased serial number in file name.
#
#        #TODO: compression
#        """
#        #Find unused filename.
#        path_n, path_c = "", ""
#        for i in range(100000):
#            path_n = path.join(self.directory, 
#                               self.make_filename(date, i, False))
#            path_c = path.join(self.directory,  
#                               self.make_filename(date, i, True))
#            if not (path.exists(path_n) or path.exists(path_c)):
#                break
#        else:
#            raise IOError("Too many files with name: " + 
#                          self.make_filename(date, None, None) +
#                          "\n    Directory: " + self.directory)
#        #Write the file
#        if compress:
#            raise IOError("Compression is not implemented.")
#        logging.debug("Writing: {}".format(path_n))
#        wfile = file(path_n, "w")
#        wfile.write(text.encode("ascii"))
#        wfile.close()
#
#
#    def read_text(self, date_start, date_end):
#        """
#        Read text files from disk.
#        
#        Reads all files from a certain date range.
#        Returns a list of strings.
#        """
#        assert isinstance(date_start, datetime)
#        assert isinstance(date_end, datetime)
#        
#        date_start = self.normalize_date(date_start)
#        date_end = self.normalize_date(date_end)
#        
#        #Get matching file names
#        date = None
#        if date_start == date_end:
#            date = date_start
#        pattern = self.make_filename(date, None, None)
#        files_glob = glob.glob1(self.directory, pattern)
##        print "files_glob:", files_glob
#        
#        #filter the useful dates and file types
#        files_filt = []
#        for fname in files_glob:
#            nameparts = fname.lower().split(".")
#            if nameparts[-1] not in ["xml", "xmlzip"]:
#                continue
#            try:
#                fdate = dateutil.parser.parse(nameparts[-3])
#                fdate = self.normalize_date(fdate)
#            except (IndexError, ValueError):
#                continue
#            if not (date_start <= fdate <= date_end):
#                continue
#            files_filt.append(fname)
##        print "files_filt:", files_filt
#        files_filt.sort()
#        
#        #read the files that have correct dates and file type
#        xml_texts = []
#        for fname in files_filt:
#            fpath = path.join(self.directory, fname)
#            logging.debug("Reading: {}".format(fpath))
#            nameparts = fname.lower().split(".")
#            extension = nameparts[-1]
#            #TODO: compression
#            if extension != "xml":
#                raise IOError("File type {0} is not implemented."
#                              .format(extension))
#            rfile = file(fpath, "r")
#            xml_texts.append(rfile.read())
#            rfile.close()
#
#        return xml_texts
#    
#    
#    def write_data(self, frame, 
#                   date_start=EARLIEST_DATE, date_end=LATEST_DATE,
#                   compress=False, overwrite=False):
#        """
#        Write a DataFrame to disk in XML format.
#        
#        Assumes that frame has a column "time", that contains ``datetime`` 
#        objects; None and nan are considered month 0.
#        """
#        assert isinstance(frame, pd.DataFrame)
#        assert isinstance(date_start, datetime)
#        assert isinstance(date_end, datetime)
#        assert isinstance(compress, bool)
#        assert isinstance(overwrite, bool)
#        
#        def month_number(date):
#            "Compute unique number for each month."
#            if date is None:
#                return 0
#            if isinstance(date, float) and isnan(date):
#                return 0
#            return date.year * 12 + date.month
#        
#        num_start = month_number(self.normalize_date(date_start))
#        num_end   = month_number(self.normalize_date(date_end))
#
#        #Split data into monthly pieces and write them.
#        month_nums = frame["time"].map(month_number)
#        groups = frame.groupby(month_nums)
#        for m_num, group in groups:
#            if num_start <= m_num <= num_end:
#                text = self.xml_converter.to_xml(group)
#                date = group["time"][0]
#                self.write_text(text, date, compress, overwrite)
#
#
#    def read_data(self, date_start=EARLIEST_DATE, date_end=LATEST_DATE):
#        """Read information from the disk, and return it as a DataFrame."""
#        assert isinstance(date_start, datetime)
#        assert isinstance(date_end, datetime)
#
#        out_frame = make_listing_frame(0)
#        texts = self.read_text(date_start, date_end)
#        for text in texts:
#            frame = self.xml_converter.from_xml(text)
#            out_frame = out_frame.append(frame, ignore_index=True, 
#                                         verify_integrity=False)
#        
#        if len(out_frame) == 0:
#            return out_frame
#        out_frame = out_frame.drop_duplicates("id", keep='last')
#        out_frame.set_index("id", drop=False, inplace=True, 
#                            verify_integrity=True)
#        return out_frame
#        
#
#
#class XmlIOSmallObject(object):
#    """
#    Store small objects as XML files.
#    
#    Trivial wrapper around open, os.rename, os.remove. Has identical interface 
#    as XmlIOBigFrame.
#    
#    Constructor Parameters
#    ----------------------
#    
#    name_prefix : str
#        String that is prepended to all file names.
#        
#    directory : str
#        Directory into which all files are written.
#        
#    xml_converter : object
#        Converts data to and from XML. Must have methods:
#        ``to_xml`` and ``from_xml``. 
#    """
#    def __init__(self, directory, name_prefix, xml_converter):
#        assert isinstance(name_prefix, basestring)
#        assert isinstance(directory, basestring)
#        assert hasattr(xml_converter, "to_xml")
#        assert hasattr(xml_converter, "from_xml")
#        self.name_prefix = name_prefix
#        self.directory = directory
#        self.xml_converter = xml_converter
#        
#    
#    def write_data(self, data):
#        """Convert data to XML, and write it to disk."""
#        assert isinstance(data, list)
#        xml_text = self.xml_converter.to_xml(data)
#        
#        #Setup file names
#        rand_str = str(random.getrandbits(32))
#        file_name = path.join(self.directory, self.name_prefix + ".xml")
#        file_new_temp = file_name + "-new-" + rand_str
#        file_old_temp = file_name + "-old-" + rand_str
#        
#        #Write file with temporary name
#        logging.debug("Writing: {}".format(file_new_temp))
#        fw = open(file_new_temp, "w")
#        fw.write(xml_text.encode("ascii"))
#        fw.close()
#        
#        #Delete files from crash, rename files, delete old file
#        try: os.remove(file_old_temp)
#        except OSError: pass
#        try: os.rename(file_name, file_old_temp)
#        except OSError: pass
#        os.rename(file_new_temp, file_name)
#        try: os.remove(file_old_temp)
#        except OSError: pass
#    
#    
#    def read_data(self):
#        """Read XML file and convert data to Python representation."""
#        file_name = path.join(self.directory, self.name_prefix + ".xml")
#        logging.debug("Reading: {}".format(file_name))
#        fr = open(file_name, "r")
#        xml_text = fr.read()
#        fr.close()
#        
#        py_data = self.xml_converter.from_xml(xml_text)
#        return py_data
#
#
#class DataStore(object):
#    """
#    Store and access the various data objects.
#    
#    Does disk IO, and adding objects at runtime.
#    """
#    def __init__(self, conf_dir=None, data_dir=None):
#        self.conf_dir = conf_dir
#        self.data_dir = data_dir
#        
#        #Containers for application data.
#        self.tasks = []
#        self.products = []
#        self.listings = make_listing_frame(0)
#        self.prices = make_price_frame(0)
#
#        #Flags for saving to disk. If True, data must be saved to disk.
#        self.products_dirty = False
#        self.tasks_dirty = False
#        self.listings_dirty = False
#        self.prices_dirty = False
#        
#    def set_products(self, products):
#        """
#        Set products to ``self.products``. tasks: list[product] | dict[_:product]
#        """
#        prod_list = products.values() if isinstance(products, dict) \
#                    else products 
#        logging.info("Setting {} products.".format(len(prod_list)))
#        self.products = prod_list
#        self.products_dirty = True
#
#    def add_tasks(self, tasks):
#        """Add tasks to ``self.tasks``. tasks: list[task] | dict[_:task]"""
#        task_list = tasks.values() if isinstance(tasks, dict) else tasks
#        logging.info("Adding {} tasks.".format(len(task_list)))
#        for task in tasks:
#            logging.debug("Adding task: '{}'".format(task.id))
#        self.tasks.extend(task_list)
#        self.tasks_dirty = True
#    
#    def merge_listings(self, listings):
#        logging.info("Merging {} listings".format(len(listings)))
#        listings["time"] = pd.to_datetime(listings["time"])
#        self.listings["time"] = pd.to_datetime(self.listings["time"])
#        self.listings = listings.combine_first(self.listings)
##        #Workaround for issue https://github.com/pydata/pandas/issues/3593
##        self.listings["time"] = pd.to_datetime(self.listings["time"])
#        self.listings_dirty = True
#    
#    def merge_prices(self, prices):
#        logging.info("Merging {} prices".format(len(prices)))
#        self.prices = prices.combine_first(self.prices)
#        #Workaround for issue https://github.com/pydata/pandas/issues/3593
#        self.prices["time"] = pd.to_datetime(self.prices["time"])
#        self.prices_dirty = True
#    
#    
#    def read_data(self, data_dir=None, 
#                  date_start=EARLIEST_DATE, date_end=LATEST_DATE):
#        """Read the data from disk."""
#        if data_dir is not None:
#            self.data_dir = data_dir
#        
#        #Load products
#        try:
#            load_prods = XmlIOSmallObject(self.data_dir, "products", 
#                                          XMLConverterProducts())
#            self.set_products(load_prods.read_data())
#        except IOError, err:
#            logging.warning("Could not load product data: " + str(err))
#
#        #Load tasks
#        try:
#            self.tasks = []
#            load_tasks = XmlIOSmallObject(self.data_dir, "tasks", 
#                                          XMLConverterTasks())
#            self.add_tasks(load_tasks.read_data())
#        except IOError, err:
#            logging.warning("Could not load task data: " + str(err))
#            
#        #Load listings
#        self.listings = make_listing_frame(0)
#        load_listings = XmlIOBigFrame(self.data_dir, "listings", 
#                                      XMLConverterListings())
#        self.merge_listings(load_listings.read_data(date_start, date_end))
#        
#        #TODO: load prices
#        
#        self.check_consistency()
#        self.products_dirty = False
#        self.tasks_dirty = False
#        self.listings_dirty = False
#    
#    
#    def write_listings(self):
#        """Write listings to disk."""
#        io_listings = XmlIOBigFrame(self.data_dir, "listings", 
#                                    XMLConverterListings())
#        io_listings.write_data(self.listings, overwrite=True)
#        self.listings_dirty = False
#    
#    def write_products(self):
#        """Write products to disk."""
#        self.products.sort(key=lambda prod: prod.id) 
#        io_products = XmlIOSmallObject(self.data_dir, "products", 
#                                       XMLConverterProducts())
#        io_products.write_data(self.products)
#        self.products_dirty = False
#        
#    def write_tasks(self):
#        """Write tasks to disk."""
#        self.tasks.sort(key=lambda task: task.id) 
#        io_tasks = XmlIOSmallObject(self.data_dir, "tasks", 
#                                    XMLConverterTasks())
#        io_tasks.write_data(self.tasks)
#        self.tasks_dirty = False
#                
#    def write_prices(self):
#        """Write prices to disk."""
#        logging.error("Writing prices is not implemented!")
#        
#    def check_consistency(self):
#        """
#        Test if the references between the various objects are consistent.
#        #TODO: consistency checks for prices
#        #TODO: test for unknown server IDs in SearchTask or listings.
#        #TODO: return inconsistencies in some format for the GUI
#        #TODO: search for tasks with duplicate IDs
#        #TODO: search for products with duplicate IDs
#        """
#        logging.debug("Testing data consistency.")
#        
#        def setn(iterable_or_none):
#            if iterable_or_none is None:
#                return set()
#            return set(iterable_or_none)
#        
#        prod_ids = set([p.id for p in self.products])
#        task_ids = set([t.id for t in self.tasks])
#   
#        for task in self.tasks:
#            #Test if task contains unknown product IDs
#            if isinstance(task, SearchTask):
#                unk_products = setn(task.expected_products) - prod_ids
#                if unk_products:    
#                    logging.warning(
#                            "Unknown product ID: '{pid}', in task '{tid}'."
#                            .format(pid="', '".join(unk_products), 
#                                    tid=task.id))
#        
#        #Test if ``self.listings`` contains unknown product, or task IDs.
#        #Iterate over all listings
#        for lid in self.listings.index:
#            found_tasks = setn(self.listings["search_tasks"][lid])
#            unk_tasks = found_tasks - task_ids
#            if unk_tasks:
#                logging.warning("Unknown task ID: '{tid}', "
#                                "in listings['search_task']['{lid}']."
#                                .format(tid="', '".join(unk_products), lid=lid))
#            found_prods = setn(self.listings["expected_products"][lid])
#            unk_products = found_prods - prod_ids
#            if unk_products:
#                logging.warning("Unknown product ID '{pid}', "
#                                "in listings['expected_products']['{lid}']."
#                                .format(pid="', '".join(unk_products), lid=lid))
#            found_prods = setn(self.listings["products"][lid])
#            unk_products = found_prods - prod_ids
#            if unk_products:
#                logging.warning("Unknown product ID '{pid}', "
#                                "in listings['products']['{lid}']."
#                                .format(pid="', '".join(unk_products), lid=lid))
#            found_prods = setn(self.listings["products_absent"][lid])
#            unk_products = found_prods - prod_ids
#            if unk_products:
#                logging.warning("Unknown product ID '{pid}', "
#                                "in listings['products_absent']['{lid}']."
#                                .format(pid="', '".join(unk_products), lid=lid))
##        logging.debug("Testing data consistency finished.")
#
#
#    @staticmethod
#    def sanitize_ids(insane_ids):
#        """
#        Sanitize string (ID) list.
#        Remove trailing and leading whitespace, remove and empty elements.
#        """
#        sane_ids = []
#        for idx in insane_ids:
#            idx = idx.strip()
#            if idx == "":
#                continue
#            sane_ids.append(idx)
#        return sane_ids
#    
#    
#    def update_expected_products(self, task_id):
#        """
#        Scan example listings that were found by the given task_id_or_number for 
#        contained products, and put them into the task_id_or_number's 'expected products' 
#        field. Then put the updated list of 'expected products' into the 
#        listings.
#        
#        TODO: explicitly respect that a listing can be found by multiple 
#              search tasks.
#              Don't overwrite the products that are expected by the other 
#              task. The algorithm currently only works as expected by chance.
#              When a search task can explicitly exclude products, it won't work
#              anymore.
#        """
#        assert isinstance(task_id, basestring)
#        #Search the right task
#        task = SearchTask("", "", "", "", "") #Dummy
#        for task in self.tasks:
#            if task.id == task_id:
#                break
#        else:
#            logging.error("Unknown task ID '{}'".format(task_id))
#            return
#        
#        logging.info("Update expected products of task: '{}'".format(task_id))
#        
#        task_expected_products = self.sanitize_ids(task.expected_products)
#        #Collect list of listings (IDs) that the search task has found.
#        #Create superset of all expected products of the training samples
#        #in this list.
#        task_listings = []
#        all_expected_products = set(task_expected_products)
#        for idx, listing in self.listings.iterrows():
#            search_tasks = listing["search_tasks"]
#            if search_tasks is None:
#                continue
#            if task_id not in search_tasks:
#                continue
#            task_listings.append(idx)
#            if listing["training_sample"] != 1:
#                continue
#            expected_products = listing["expected_products"]
#            if expected_products is None:
#                continue
#            all_expected_products.update(expected_products)
#        
#        #Create list of all products, but order of products already in 
#        #list is preserved
#        for prod_id in task_expected_products:
#            try:
#                all_expected_products.remove(prod_id)
#            except KeyError:
#                pass
#        new_prods = list(all_expected_products)
#        new_prods.sort()
#        new_prods = task.expected_products + new_prods
#        
#        #Put list of new products into task and listings
#        task.expected_products = new_prods
#        new_listings = make_listing_frame(index=task_listings)
#        for idx in task_listings:
#            new_listings.set_value(idx, "expected_products", new_prods)
#        self.merge_listings(new_listings)
#
#        self.tasks_dirty = True
#        self.listings_dirty = True
#
#
#    def write_expected_products_to_listings(self, task_id):
#        """
#        Copy value of ``expected_products`` from the specified task to all
#        related listings. Related listings are listings that were fund by
#        this task.
#        
#        TODO: respect that a listing can be found by multiple search tasks.
#              Don't overwrite the products that are expected by the other 
#              task. 
#        """
#        assert isinstance(task_id, basestring)
#        #Search the right task
#        task = SearchTask("", "", "", "", "") #Dummy
#        for task in self.tasks:
#            if task.id == task_id:
#                break
#        else:
#            logging.error("Unknown task ID '{}'".format(task_id))
#            return
#        
#        logging.info("Set expected products of task: '{}'".format(task_id))
#        
#        #Get list of IDs of of listings that were found by this task
#        my_listings = []
#        for idx, listing in self.listings.iterrows():
#            search_tasks = listing["search_tasks"]
#            if search_tasks is None or task_id not in search_tasks:
#                continue
#            my_listings.append(idx)
#        
#        #Put list of expected products from task into listings
#        task_expected_products = self.sanitize_ids(task.expected_products)
#        new_listings = make_listing_frame(index=my_listings)
#        new_listings["expected_products"].fill(task_expected_products)
#        self.merge_listings(new_listings)
#        
#        self.listings_dirty = True
        
