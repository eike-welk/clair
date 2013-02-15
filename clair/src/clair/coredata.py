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
from datetime import datetime, timedelta
from types import NoneType
import random
from dateutil.parser import parse as parse_date 
from dateutil.relativedelta import relativedelta
from numpy import nan
import pandas as pd
from lxml import etree, objectify



def make_listing_frame(nrows):
    """
    Create empty DataFrame with `nrows` listings/auctions.
    
    Each row represents a listing. The columns represent the listing's 
    attributes. The object contains no data, nearly all values are None or nan.
    
    TODO: Put into central location. 
    """
    index=[str(i) for i in range(nrows)]
    
    listings = pd.DataFrame(index=index)
    listings["id"]                = None  #internal unique ID of each listing.
    listings["training_sample"]   = False #This is training sample if True
    listings["query_string"]      = None  #String with search keywords
    listings["expected_products"] = None  #list of product IDs
    
    listings["products"]    = None  #Products in this listing. List of DetectedProduct

    listings["thumbnail"]   = None          
    listings["image"]       = None          
    
    listings["title"]       = None
    listings["description"] = None
    #TODO: include ``ItemSpecifics``: name value pairs eg.: {"megapixel": "12"}
    #TODO: include bid_count?
    listings["active"]      = nan   #you can still buy it if True
    listings["sold"]        = nan   #successful sale if True
    listings["currency"]    = None  #currency for price EUR, USD, ...
    listings["price"]       = nan   #price of all items in listing
    listings["shipping"]    = nan   #shipping cost
    listings["type"]        = None  #auction, fixed-price, unknown
    listings["time"]        = None  #Time when price is/was valid. End time in case of auctions
    listings["location"]    = None  #Location of item (pre sale)
    listings["postcode"]    = None  #Postal code of location
    listings["country"]     = None  #Country of item location
    listings["condition"]   = nan   #1.: new, 0.: completely unusable
    
    listings["server"]      = None  #string to identify the server
    listings["server_id"]   = None  #ID of listing on the server
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



class Product(Record):
    """"A product that a company produces."""
    def __init__(self, id, name, description="", #IGNORE:W0622
                 important_words=None, categories=None):
        Record.__init__(self)
        assert isinstance(id, str)
        assert isinstance(name, str)
        assert isinstance(description, str)
        assert isinstance(important_words, (list, NoneType))
        assert isinstance(categories, (list, NoneType))
        self.id = id
        self.name = name
        self.description = description
        self.important_words = important_words
        self.categories = categories



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
    E = objectify.E

    def to_xml_list(self, tag, el_list):
        """Convert lists, wrap each element of a list with a tag."""
        if el_list is None:
            return [None]
        E = self.E
        node = getattr(E, tag)
        xml_nodes = [node(el) for el in el_list]
        return xml_nodes
    
    
    def from_xml_list(self, tag, xml_list):
        """Convert a repetition of XML elements into a Python list."""
        if isinstance(xml_list, objectify.NoneElement):
            return None
        
        elements = xml_list[tag]
        el_list = []
        for el in elements:
            #TODO: convert structured elements.
            el_list.append(el.pyval)
        return el_list



class ListingsXMLConverter(XMLConverter):
    """
    Convert listings to and from XML
    
    TODO: XML escapes for description
    http://wiki.python.org/moin/EscapingXml
    """
    def to_xml(self, listings):
        """Convert DataFrame with listings/auctions to XML."""
        E = self.E

        root_xml = E.listings(
            E.version("0.1") )
        for i in range(len(listings.index)):
            li = listings.ix[i]
            li_xml = E.listing(
                E.id(li["id"]),
                E.training_sample(bool(li["training_sample"])),
                E.query_string(li["query_string"]),
                E.expected_products(*self.to_xml_list(
                                        "product", li["expected_products"])),
                E.products(*self.to_xml_list("product", li["products"])),
                E.thumbnail(li["thumbnail"]),
                E.image(li["image"]),
                E.title(li["title"]),
                E.description(li["description"]),
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
                E.url_webui(li["url_webui"]) )
            root_xml.append(li_xml)
        
#        doc_xml = etree.ElementTree(root_xml)
        doc_str = etree.tostring(root_xml, pretty_print=True)
        return doc_str 
        
        
    def from_xml(self, xml):
        """Convert XML string into DataFrame with listings/auctions"""
        root_xml = objectify.fromstring(xml)
#        print objectify.dump(root_xml)
        
        version = root_xml.version.text
        assert version == "0.1"
               
        listing_xml = root_xml.listing
        nrows = len(listing_xml)
        listings = make_listing_frame(nrows)
        for i, li in enumerate(listing_xml):    
            listings["id"][i] = li.id.pyval 
            listings["training_sample"][i] = li.training_sample.pyval 
            listings["query_string"][i] = li.query_string.pyval
            listings["expected_products"][i] = self.from_xml_list(
                                            "product", li.expected_products)
            listings["products"][i] = self.from_xml_list(
                                            "product", li.products)
            listings["thumbnail"][i] = li.thumbnail.pyval
            listings["image"][i] = li.image.pyval
            listings["title"][i] = li.title.pyval 
            listings["description"][i] = li.description.pyval
            listings["active"][i] = li.active.pyval
            listings["sold"][i] = li.sold.pyval
            listings["currency"][i] = li.currency.pyval
            listings["price"][i]    = li.price.pyval
            listings["shipping"][i] = li.shipping.pyval
            listings["type"][i] = li.type.pyval
            listings["time"][i] = parse_date(li.time.pyval) \
                                  if li.time.pyval is not None else None
            listings["location"][i] = li.location.pyval
            listings["postcode"][i] = li.postcode.pyval
            listings["country"][i] = li.country.pyval
            listings["condition"][i] = li.condition.pyval
            listings["server"][i] = li.server.pyval
            listings["server_id"][i] = li.server_id.pyval #ID of listing on server
#            listings["data_directory"] = ""
            listings["url_webui"][i] = li.url_webui.pyval
#            listings["server_repr"][i] = nan

        #Put our IDs into index
        listings.set_index("id", drop=False, inplace=True, 
                           verify_integrity=True)
        return listings



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
    def __init__(self, name_prefix, directory, xml_converter):
        assert isinstance(name_prefix, basestring)
        assert isinstance(directory, basestring)
        
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
        num_str = "{:0>2d}".format(number) if number is not None else "*"
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
              
        #TODO: overwrite
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
        files_old_temp = map(lambda f: f + "-old-" + rand_str, files_old)
        #make file name(s) for new file
        file_new = path.join(self.directory,
                             self.make_filename(date, 0, compress))
        file_new_temp = file_new + "-new-" + rand_str
        
        #Write file with temporary name
        print "Writing:", file_new_temp #TODO: logging
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
        for i in range(100):
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
        print "Writing:", path_n #TODO: logging
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
                fdate = parse_date(nameparts[-3])
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
            print "Reading:", fpath #TODO: logging
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
    
    
    def write_dataframe(self, frame, 
                        date_start=EARLIEST_DATE, date_end=LATEST_DATE,
                        compress=False, overwrite=False):
        """
        Write a DataFrame to disk in XML format.
        
        Assumes that frame has a column "time", that contains ``datetime`` 
        and no None.
        """
        assert isinstance(frame, pd.DataFrame)
        assert isinstance(date_start, datetime)
        assert isinstance(date_end, datetime)
        assert isinstance(compress, bool)
        assert isinstance(overwrite, bool)
        
        def month_number(date):
            "Compute unique number for each month."
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


    def read_dataframe(self, date_start=EARLIEST_DATE, date_end=LATEST_DATE):
        """Read information from the disk, and return it as a DataFrame."""
        assert isinstance(date_start, datetime)
        assert isinstance(date_end, datetime)

        out_frame = pd.DataFrame()
        texts = self.read_text(date_start, date_end)
        for text in texts:
            frame = self.xml_converter.from_xml(text)
            out_frame = out_frame.append(frame, ignore_index=True, 
                                         verify_integrity=False)
            
        out_frame = out_frame.drop_duplicates("id", take_last=True)
        out_frame.set_index("id", drop=False, inplace=True, 
                            verify_integrity=True)
        return out_frame
        
