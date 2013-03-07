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
Put module description here.
"""

from __future__ import division
from __future__ import absolute_import              

import os
import os.path as path
import glob
from datetime import datetime #, timedelta
from types import NoneType
import random
import dateutil
from logging import debug, info, warning, error, critical
#from dateutil.parser import parse as parse_date 
#from dateutil.relativedelta import relativedelta

from numpy import nan, isnan
import pandas as pd
from lxml import etree, objectify



def make_listing_frame(nrows):
    """
    Create empty DataFrame with `nrows` listings/auctions.
    
    Each row represents a listing. The columns represent the listing's 
    attributes. The object contains no data, nearly all values are None or nan.
    """
    index=[str(i) for i in range(nrows)]
    
    listings = pd.DataFrame(index=index)
    listings["id"]                = None  #internal unique ID of each listing.
    listings["training_sample"]   = nan   #This is training sample if True
#    listings["query_string"]      = None  #String with search keywords
    listings["search_task"]       = None  #ID (string) of search task, 
                                          #    that returned this listing
    listings["expected_products"] = None  #list of product IDs (strings)
    
    listings["products"]          = None  #Products in this listing. 
    listings["products_absent"]   = None  #Products not in this listing. 
                                          #    List of product IDs (strings)

    listings["thumbnail"]   = None  #URL of small image
    listings["image"]       = None  #URL of large image
    
    listings["title"]       = None  #Short description of listing.
    listings["description"] = None  #Long description of listing.
    listings["prod_spec"]   = None  #product specific name value pairs (dict)
                                    #    for example {"megapixel": "12"};
                                    #    the ``ItemSpecifics`` on Ebay
    #TODO: include bid_count?
    listings["active"]      = nan   #you can still buy it if True
    listings["sold"]        = nan   #successful sale if True
    listings["currency"]    = None  #currency for price EUR, USD, ...
    listings["price"]       = nan   #price of listing (all items together)
    listings["shipping"]    = nan   #shipping cost
    listings["type"]        = None  #auction, fixed-price, unknown
    listings["time"]        = None  #Time when price is/was valid. End time in case of auctions
    listings["location"]    = None  #Location of item (pre sale)
    listings["postcode"]    = None  #Postal code of location
    listings["country"]     = None  #Country of item location
    listings["condition"]   = nan   #1.: new, 0.: completely unusable
    #TODO: listings["seller"]     = None  #User name of seller
    #TODO: listings["buyer"]      = None  
    
    listings["server"]      = None  #string to identify the server
    listings["server_id"]   = None  #ID of listing on the server
    #TODO: rename to "is_final_price"
    listings["final_price"] = nan   #If True: This is the final price of the auction.
#    listings["data_dir"]    = None  #Images, html, ... might be stored here
    listings["url_webui"]   = None  #Link to web representation of listing.
#    listings["server_repr"] = None  #representation of listing on server (XML)

    return  listings
    


class Record(object):
    """
    Base class for classes that contain mainly data. Somewhat analogous 
    to namedtuple, but mutable.
    """
    def __init__(self, **params):
        for name, value in params.iteritems():
            setattr(self, name, value)

    def __repr__(self):
        """Convert object to string. Called by ``print``."""
        out_str = self.__class__.__name__ + "("
        
        names = self.__dict__.keys()
        names.sort()
        if "id" in names:
            names.remove("id")
            out_str += "\n    id = {0},".format(repr(self.__dict__["id"]))
        for name in names:
            out_str += "\n    {0} = {1},".format(name, repr(self.__dict__[name]))
            
        out_str += ")\n"
        return out_str
    
    def __eq__(self, other):
        """
        Compare this record to an other record. Test for equality.
        
        An object is considered equal if its data attributes are equal.
        """
        if len(self.__dict__) != len(other.__dict__):
            return False
        for name, value in self.__dict__.iteritems():
            if not (other.__dict__[name] == value):
                return False
        
        return True
    
    def __ne__(self, other):
        """Compare record to other record. Test for inequality."""
        return not self.__eq__(other)



class Product(Record):
    """Data about a single product."""
    #Tool tips are used by QT
    tool_tips = {
        "id":
            "<p>Product ID. Should not contain spaces.</p>"
            "<p><b>Warning!</b> Changing product IDs is problematic."
            "They are used in <i>listings</i>, <i>prices</i>, and "
            "<i>tasks</i>.</p>",
        "name":
            "Product name. A single line of text.",
        "important_words":
            "<p>Important patterns for the text recognition algorithms.</p>"
            "<p>Each line is one pattern. The patterns can contain spaces.</p>",
        "categories":
            "Categories for grouping products. Each line is one category.",
        "description":
            "Description of the product. Any text."}
    
    def __init__(self, id="", name="", description="", #IGNORE:W0622
                 important_words=None, categories=None):
        Record.__init__(self)
        assert isinstance(id, basestring)
        assert isinstance(name, basestring)
        assert isinstance(description, basestring)
        assert isinstance(important_words, (list, NoneType))
        assert isinstance(categories, (list, NoneType))
        self.id = id
        self.name = name
        self.description = description
        self.important_words = important_words if important_words is not None \
                               else [] 
        self.categories = categories if categories is not None else []



class SearchTask(Record):
    """Task to search for listings on a certain server."""
    def __init__(self, id, due_time, server, query_string, #IGNORE:W0622
                 recurrence_pattern=None, n_listings=100,
                 price_min=None, price_max=None, currency="EUR",
                 expected_products=None):
        Record.__init__(self)
        self.id = id
        self.due_time = due_time
        self.server = server
        self.recurrence_pattern = recurrence_pattern
        self.query_string = query_string
        self.n_listings = n_listings
        self.price_min = price_min
        self.price_max = price_max
        self.currency = currency
        self.expected_products = expected_products



class UpdateTask(Record):
    """Task to update listings on a certain server."""
    def __init__(self, id, due_time, server, #IGNORE:W0622
                 recurrence_pattern=None, listings=None):
        Record.__init__(self)
        self.id = id
        self.due_time = due_time
        self.server = server
        self.recurrence_pattern = recurrence_pattern
        self.listings = listings if listings is not None else []



class XMLConverter(object):
    """
    Base class for objects that convert to and from XML
    
    Unicode introduction
    http://docs.python.org/2/howto/unicode.html
    
    TODO:
    Generic converter Python <-> XML
    
    https://github.com/dmw/pyxser
    http://pyxml.sourceforge.net/topics/howto/node26.html
    """
    E = objectify.ElementMaker(
            annotate=False, 
            nsmap={"xsi":"http://www.w3.org/2001/XMLSchema-instance"})

    def to_xml_list(self, tag, el_list):
        """Convert lists, wrap each element of a list with a tag."""
        if el_list is None:
            return [None]
        if isinstance(el_list, float) and isnan(el_list):
            return [None]
        E = self.E
        node = getattr(E, tag)
        xml_nodes = [node(el) for el in el_list]
        return xml_nodes
    
    
    def from_xml_list(self, tag, xml_list):
        """Convert a repetition of XML elements into a Python list."""
        if isinstance(xml_list, objectify.NoneElement):
            return None
        
        try:
            elements = xml_list[tag]
        except AttributeError:
            return []
        
        el_list = []
        for el in elements:
            #TODO: convert structured elements.
            el_list.append(el.pyval)
        return el_list
    
    
    def to_xml_dict(self, py_dict):
        """Convert a dict to a XML structure"""
        if py_dict is None:
            return [None]
        if isinstance(py_dict, float) and isnan(py_dict):
            return [None]
        E = self.E
        xml_dict_repr = [E.kv_pair(E.key(k), E.value(v)) 
                         for k, v in py_dict.iteritems()]
        return xml_dict_repr
    
    
    def from_xml_dict(self, xml_dict):
        """Convert a special XML structure to a dict."""
        if isinstance(xml_dict, objectify.NoneElement):
            return None
        ustrn = self.unicode_or_none
        
        py_dict = {}
        xml_kv_pairs = xml_dict.kv_pair
        for xml_kv_pair in xml_kv_pairs:
            key = ustrn(xml_kv_pair.key.pyval)
            value = ustrn(xml_kv_pair.value.pyval)
            py_dict[key] = value
            
        return py_dict
    
    
    def unicode_or_none(self, value):
        """
        Convert value to a unicode string, but if value is None return None.
        """
        if value is None:
            return None
        else:
            return unicode(value)


    def datetime_or_none(self, str_none):
        """
        Convert ``str_none`` to ``datetime``, but if it is None return None.
        """
        if str_none is None:
            return None
        else:
            return dateutil.parser.parse(str_none)
        
        
    def float_or_none(self, float_none):
        """
        Convert ``float_none`` to ``float``, but if it is None return None.
        """
        if float_none is None:
            return None
        else:
            return float(float_none)
        
        
    def int_or_none(self, int_none):
        """
        Convert ``int_none`` to ``int``, but if it is None return None.
        """
        if int_none is None:
            return None
        else:
            return int(int_none)
        
        

class ListingsXMLConverter(XMLConverter):
    """
    Convert listings to and from XML
    
    TODO: XML escapes for description
    http://wiki.python.org/moin/EscapingXml
    """
    def to_xml(self, listings):
        """Convert DataFrame with listings/auctions to XML."""
        E = self.E

        root_xml = E.listing_storage(
            E.version("0.1"),
            E.listings())
        for i in range(len(listings.index)):
            li = listings.ix[i]
            li_xml = E.listing(
                E.id(li["id"]),
                E.training_sample(float(li["training_sample"])),
                E.search_task(li["search_task"]),
#                E.query_string(li["query_string"]),
                E.expected_products(*self.to_xml_list(
                                        "product", li["expected_products"])),
                E.products(*self.to_xml_list("product", li["products"])),
                E.products_absent(*self.to_xml_list(
                                        "product", li["products_absent"])),
                E.thumbnail(li["thumbnail"]),
                E.image(li["image"]),
                E.title(li["title"]),
                E.description(li["description"]),
                E.prod_spec(*self.to_xml_dict(li["prod_spec"])),
                E.active(float(li["active"])),
                E.sold(float(li["sold"])),
                E.currency(li["currency"]),
                E.price(float(li["price"])),
                E.shipping(float(li["shipping"])),
                E.type(li["type"]),
                E.time(li["time"]),
                E.location(li["location"]),
                E.postcode(li["postcode"]),
                E.country(li["country"]),
                E.condition(float(li["condition"])),
                E.server(li["server"]),
                E.server_id(li["server_id"]),
                E.final_price(float(li["final_price"])),
                E.url_webui(li["url_webui"]) )
            root_xml.listings.append(li_xml)
        
#        doc_xml = etree.ElementTree(root_xml)
        doc_str = etree.tostring(root_xml, pretty_print=True)
        return doc_str 
        
        
    def from_xml(self, xml):
        """Convert XML string into DataFrame with listings/auctions"""
        ustr = self.unicode_or_none
        parse_date = self.datetime_or_none
        
        root_xml = objectify.fromstring(xml)
#        print objectify.dump(root_xml)
        version = root_xml.version.text
        assert version == "0.1"
        
        listing_xml = root_xml.listings.listing
        nrows = len(listing_xml)
        listings = make_listing_frame(nrows)
        for i, li in enumerate(listing_xml):    
            listings["id"][i] = ustr(li.id.pyval) 
            listings["training_sample"][i] = li.training_sample.pyval
            listings["search_task"][i] = ustr(li.search_task.pyval)
#            listings["query_string"][i] = ustr(li.query_string.pyval)
            listings["expected_products"][i] = self.from_xml_list(
                                            "product", li.expected_products)
            listings["products"][i] = self.from_xml_list(
                                            "product", li.products)
            try: listings["products_absent"][i] = self.from_xml_list(
                                            "product", li.products_absent)
            except AttributeError: pass
            listings["thumbnail"][i] = ustr(li.thumbnail.pyval)
            listings["image"][i] = ustr(li.image.pyval)
            listings["title"][i] = ustr(li.title.pyval )
            listings["description"][i] = ustr(li.description.pyval)
            listings["prod_spec"][i] = self.from_xml_dict(li.prod_spec)
            listings["active"][i] = li.active.pyval
            listings["sold"][i] = li.sold.pyval
            listings["currency"][i] = ustr(li.currency.pyval)
            listings["price"][i]    = li.price.pyval
            listings["shipping"][i] = li.shipping.pyval
            listings["type"][i] = ustr(li.type.pyval)
            listings["time"][i] = parse_date(li.time.pyval)
            listings["location"][i] = ustr(li.location.pyval)
            listings["postcode"][i] = ustr(li.postcode.pyval)
            listings["country"][i] = ustr(li.country.pyval)
            listings["condition"][i] = li.condition.pyval
            listings["server"][i] = ustr(li.server.pyval)
            listings["server_id"][i] = ustr(li.server_id.pyval) #ID of listing on server
            listings["final_price"][i] = li.final_price.pyval
#            listings["data_directory"] = ""
            listings["url_webui"][i] = ustr(li.url_webui.pyval)
#            listings["server_repr"][i] = nan

        #Put our IDs into index
        listings.set_index("id", drop=False, inplace=True, 
                           verify_integrity=True)
        return listings



class ProductXMLConverter(XMLConverter):
    """Convert a dictionary of Product objects to and from XML"""
    def to_xml(self, product_dict):
        """Convert dictionary of Product to XML"""
        E = self.E

        root_xml = E.product_storage(
            E.version("0.1"),
            E.products())
        for pr in product_dict.values():
            pr_xml = E.product(
                E.id(pr.id),
                E.name(pr.name),
                E.description(pr.description),
                E.important_words(*self.to_xml_list("word", 
                                                    pr.important_words)),
                E.categories(*self.to_xml_list("category", pr.categories)),
                )
            root_xml.products.append(pr_xml)
        
        doc_str = etree.tostring(root_xml, pretty_print=True)
        return doc_str 

        
    def from_xml(self, xml):
        """Convert from XML representation to dictionary of Product."""
        root_xml = objectify.fromstring(xml)
#        print objectify.dump(root_xml)
        version = root_xml.version.text
        assert version == "0.1"
               
        product_xml = root_xml.products.product
        product_dict = {}
        for pr in product_xml:    
            prod = Product(id=pr.id.pyval,
                           name=pr.name.pyval,
                           description=pr.description.pyval,
                           important_words=self.from_xml_list(
                                                "word", pr.important_words),
                           categories=self.from_xml_list(
                                                "category", pr.categories))
            product_dict[prod.id] = prod
        
        return product_dict



class TaskXMLConverter(XMLConverter):
    """
    Convert task objects to and from XML
    
    Currently only stores SearchTask objects.
    """
    def to_xml(self, tasks):
        """Convert dictionary or list of tasks to XML"""
        E = self.E
        task_list = tasks.values() if isinstance(tasks, dict) else tasks

        root_xml = E.task_storage(
            E.version("0.1"),
            E.tasks())
        for tsk in task_list:
            if not isinstance(tsk, SearchTask):
                continue
            tsk_xml = E.search_task(
                E.id(tsk.id),
                E.due_time(tsk.due_time),
                E.server(tsk.server),
                E.recurrence_pattern(tsk.recurrence_pattern),
                E.query_string(tsk.query_string),
                E.n_listings(tsk.n_listings),
                E.price_min(tsk.price_min),
                E.price_max(tsk.price_max),
                E.currency(tsk.currency),
                E.expected_products(*self.to_xml_list("product", 
                                                      tsk.expected_products))
                )
            root_xml.tasks.append(tsk_xml)
        
        doc_str = etree.tostring(root_xml, pretty_print=True)
        return doc_str 

        
    def from_xml(self, xml):
        """Convert from XML representation to dictionary of Product."""
        ustrn = self.unicode_or_none
        parse_date = self.datetime_or_none
        floatn = self.float_or_none
        intn = self.int_or_none
        
        root_xml = objectify.fromstring(xml)
#        print objectify.dump(root_xml)
        version = root_xml.version.text
        assert version == "0.1"
               
        task_xml = root_xml.tasks.search_task
        task_dict = {}
        for tsk in task_xml:    
            prod = SearchTask(id=tsk.id.pyval,
                              due_time=parse_date(tsk.due_time.pyval), 
                              server=ustrn(tsk.server.pyval), 
                              recurrence_pattern=ustrn(
                                                tsk.recurrence_pattern.pyval), 
                              query_string=ustrn(tsk.query_string.pyval), 
                              n_listings=intn(tsk.n_listings.pyval), 
                              price_min=floatn(tsk.price_min.pyval), 
                              price_max=floatn(tsk.price_max.pyval), 
                              currency=ustrn(tsk.currency.pyval), 
                              expected_products=self.from_xml_list(
                                        "product", tsk.expected_products)
                              )
            task_dict[prod.id] = prod
        
        return task_dict



#Earliest and latest possible date for ``datetime``
EARLIEST_DATE = datetime(1, 1, 1)
LATEST_DATE = datetime(9999, 12, 31) 

class XmlBigFrameIO(object):
    """
    Store big DataFrame objects as XML files.
    
    Assumes that the DataFrame has "time" and "id" columns. The data is split
    into chunks, that are stored in separate files. Each chunk contains the 
    data of one month. IDs must be unique. If there are multiple rows with 
    the same ID, only the last row is kept.
    
    Constructor Parameters
    ----------------------
    
    name_prefix : str
        String that is prepended to all file names.
        
    directory : str
        Directory into which all files are written.
        
    xml_converter : object
        Converts DataFrame to and from XML. Must have methods:
        ``to_xml`` and ``from_xml``. 
    """
    def __init__(self, directory, name_prefix, xml_converter):
        assert isinstance(name_prefix, basestring)
        assert isinstance(directory, basestring)
        if xml_converter is not None:
            assert hasattr(xml_converter, "to_xml")
            assert hasattr(xml_converter, "from_xml")
        
        self.name_prefix = name_prefix
        self.directory = directory
        self.xml_converter = xml_converter
        
    
    def normalize_date(self, date):
        """Set all fields of ``date`` to 0 except ``year`` and ``month``."""
        return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    
    def make_filename(self, date, number, compress):
        """
        Create a filename or glob pattern
        """
        date_str = date.strftime("%Y-%m") if date is not None else "*"
        #http://docs.python.org/2/library/string.html#formatstrings
        num_str = "{:0>3d}".format(number) if number is not None else "*"
        if compress == True:
            ext_str = "xmlzip"
        elif compress == False:
            ext_str = "xml"
        else:
            ext_str = "*"
            
        filename = "{pref}.{date}.{num}.{ext}".format(pref=self.name_prefix,
                                                      date=date_str,
                                                      num=num_str,
                                                      ext=ext_str)
        return filename
        
        
    def write_text(self, text, date, compress, overwrite):
        """
        Write text file to disk.
        
        Parameter
        ----------
        
        text : str, unicode
            Contents of file
            
        date : datetime
            Used asa part of file name 
            
        compress : bool
            Compress the file's contents.
        
        overwrite : bool
            Don't overwrite existing file, but create additional file with
            increased serial number in file name.
        
        #TODO: compression
        """
        assert isinstance(text, basestring)
        assert isinstance(date, datetime)
        assert isinstance(compress, bool)
        assert isinstance(overwrite, bool)
        
        if overwrite:
            self._write_text_overwrite(text, date, compress)
        else:
            self._write_text_new_file(text, date, compress)
        
    
    def _write_text_overwrite(self, text, date, compress):
        """
        Write text file to disk.
        
        Overwrite existing file, delete all other files with same prefix
        and date in file name.

        #TODO: compression
        """
        rand_str = str(random.getrandbits(32))
        #Get existing file for specified month, create temporary names for them
        file_pattern = path.join(self.directory, 
                                 self.make_filename(date, None, None))
        files_old = glob.glob(file_pattern)
        files_old_temp = [f + "-old-" + rand_str for f in files_old]
        #make file name(s) for new file
        file_new = path.join(self.directory,
                             self.make_filename(date, 0, compress))
        file_new_temp = file_new + "-new-" + rand_str
        
        #Write file with temporary name
        debug("Writing: {}".format(file_new_temp))
        fw = open(file_new_temp, "w")
        fw.write(text.encode("ascii"))
        fw.close()
        
        #Rename old files 
        for f_old, f_temp in zip(files_old, files_old_temp):
            os.rename(f_old, f_temp)
        #Rename new file to final name
        os.rename(file_new_temp, file_new)
        #Delete old files
        for f_temp in files_old_temp:
            os.remove(f_temp)
    
    
    def _write_text_new_file(self, text, date, compress):
        """
        Write text file to disk.
        
        Doesn't overwrite existing file, but create additional file with
        increased serial number in file name.

        #TODO: compression
        """
        #Find unused filename.
        path_n, path_c = "", ""
        for i in range(10000):
            path_n = path.join(self.directory, 
                               self.make_filename(date, i, False))
            path_c = path.join(self.directory,  
                               self.make_filename(date, i, True))
            if not (path.exists(path_n) or path.exists(path_c)):
                break
        else:
            raise IOError("Too many files with name: " + 
                          self.make_filename(date, None, None) +
                          "\n    Directory: " + self.directory)
        #Write the file
        if compress:
            raise IOError("Compression is not implemented.")
        debug("Writing: {}".format(path_n))
        wfile = file(path_n, "w")
        wfile.write(text.encode("ascii"))
        wfile.close()


    def read_text(self, date_start, date_end):
        """
        Read text files from disk.
        
        Reads all files from a certain date range.
        Returns a list of strings.
        """
        assert isinstance(date_start, datetime)
        assert isinstance(date_end, datetime)
        
        date_start = self.normalize_date(date_start)
        date_end = self.normalize_date(date_end)
        
        #Get matching file names
        date = None
        if date_start == date_end:
            date = date_start
        pattern = self.make_filename(date, None, None)
        files_glob = glob.glob1(self.directory, pattern)
#        print "files_glob:", files_glob
        
        #filter the useful dates and file types
        files_filt = []
        for fname in files_glob:
            nameparts = fname.lower().split(".")
            if nameparts[-1] not in ["xml", "xmlzip"]:
                continue
            try:
                fdate = dateutil.parser.parse(nameparts[-3])
                fdate = self.normalize_date(fdate)
            except (IndexError, ValueError):
                continue
            if not (date_start <= fdate <= date_end):
                continue
            files_filt.append(fname)
#        print "files_filt:", files_filt
        files_filt.sort()
        
        #read the files that have correct dates and file type
        xml_texts = []
        for fname in files_filt:
            fpath = path.join(self.directory, fname)
            debug("Reading: {}".format(fpath))
            nameparts = fname.lower().split(".")
            extension = nameparts[-1]
            #TODO: compression
            if extension != "xml":
                raise IOError("File type {0} is not implemented."
                              .format(extension))
            rfile = file(fpath, "r")
            xml_texts.append(rfile.read())
            rfile.close()

        return xml_texts
    
    
    def write_data(self, frame, 
                        date_start=EARLIEST_DATE, date_end=LATEST_DATE,
                        compress=False, overwrite=False):
        """
        Write a DataFrame to disk in XML format.
        
        Assumes that frame has a column "time", that contains ``datetime`` 
        objects; None and nan are considered month 0.
        """
        assert isinstance(frame, pd.DataFrame)
        assert isinstance(date_start, datetime)
        assert isinstance(date_end, datetime)
        assert isinstance(compress, bool)
        assert isinstance(overwrite, bool)
        
        def month_number(date):
            "Compute unique number for each month."
            if date is None:
                return 0
            if isinstance(date, float) and isnan(date):
                return 0
            return date.year * 12 + date.month
        
        num_start = month_number(self.normalize_date(date_start))
        num_end   = month_number(self.normalize_date(date_end))

        #Split data into monthly pieces and write them.
        month_nums = frame["time"].map(month_number)
        groups = frame.groupby(month_nums)
        for m_num, group in groups:
            if num_start <= m_num <= num_end:
                text = self.xml_converter.to_xml(group)
                date = group["time"][0]
                self.write_text(text, date, compress, overwrite)


    def read_data(self, date_start=EARLIEST_DATE, date_end=LATEST_DATE):
        """Read information from the disk, and return it as a DataFrame."""
        assert isinstance(date_start, datetime)
        assert isinstance(date_end, datetime)

        out_frame = make_listing_frame(0)
        texts = self.read_text(date_start, date_end)
        for text in texts:
            frame = self.xml_converter.from_xml(text)
            out_frame = out_frame.append(frame, ignore_index=True, 
                                         verify_integrity=False)
        
        if len(out_frame) == 0:
            return out_frame
        out_frame = out_frame.drop_duplicates("id", take_last=True)
        out_frame.set_index("id", drop=False, inplace=True, 
                            verify_integrity=True)
        return out_frame
        


class XmlSmallObjectIO(object):
    """
    Store small objects as XML files.
    
    Trivial wrapper around open, os.rename, os.remove. Has identical interface 
    as XmlBigFrameIO.
    
    Constructor Parameters
    ----------------------
    
    name_prefix : str
        String that is prepended to all file names.
        
    directory : str
        Directory into which all files are written.
        
    xml_converter : object
        Converts data to and from XML. Must have methods:
        ``to_xml`` and ``from_xml``. 
    """
    def __init__(self, directory, name_prefix, xml_converter):
        assert isinstance(name_prefix, basestring)
        assert isinstance(directory, basestring)
        assert hasattr(xml_converter, "to_xml")
        assert hasattr(xml_converter, "from_xml")
        self.name_prefix = name_prefix
        self.directory = directory
        self.xml_converter = xml_converter
        
    
    def write_data(self, data):
        """Convert data to XML, and write it to disk."""
        xml_text = self.xml_converter.to_xml(data)
        
        #Setup file names
        rand_str = str(random.getrandbits(32))
        file_name = path.join(self.directory, self.name_prefix + ".xml")
        file_new_temp = file_name + "-new-" + rand_str
        file_old_temp = file_name + "-old-" + rand_str
        
        #Write file with temporary name
        debug("Writing: {}".format(file_new_temp))
        fw = open(file_new_temp, "w")
        fw.write(xml_text.encode("ascii"))
        fw.close()
        
        #Delete files from crash, rename files, delete old file
        try: os.remove(file_old_temp)
        except OSError: pass
        try: os.rename(file_name, file_old_temp)
        except OSError: pass
        os.rename(file_new_temp, file_name)
        try: os.remove(file_old_temp)
        except OSError: pass
    
    
    def read_data(self):
        """Read XML file and convert data to Python representation."""
        file_name = path.join(self.directory, self.name_prefix + ".xml")
        debug("Reading: {}".format(file_name))
        fr = open(file_name, "r")
        xml_text = fr.read()
        fr.close()
        
        py_data = self.xml_converter.from_xml(xml_text)
        return py_data
