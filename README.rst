##############################################
Clair
##############################################

Clair is a project to collect prices on E-Commerce sites, and display them in graphical form. 
It is aimed at used goods, that are not labeled with product IDs, but that are described with natural languages. 
Product recognition is semi automatic and uses natural language processing. 

Clair is named after Wesley Clair Mitchell, an important US economist, 
who mainly worked empirically and collected a big database of prices.
Mitchell also believed that markets need to be regulated, 
and was influential in creating the New Deal.

Software
=======================================

The software is currently in an early beta stage. 
There are no components usable for end users, but there are crude programs, 
that can be tested without much effort.

Clair is written in Python, the GUI parts use the *Qt* framework. 
It can currently only communicate with Ebay.
Clair consists of a set of libraries, that can be used in other software, and
(fairly crude) applications:

``clairdaemon``
    A daemon that downloads listings from the internet, 
    identifies products in them, and writes everything to disk. 

``clairgui`` 
    A graphical application for manipulation of the stored data. 

Installation and Usage
=======================================

Clair needs fairly many libraries to function:

**Requests**
    A HTTP library, needed by *python-ebay*.
    http://docs.python-requests.org/en/latest/

**python-ebay**
    A library to communicate with Ebay over the Internet.
    https://github.com/roopeshvaddepally/python-ebay
    
**LXML**
    A XML parsing library.
    http://lxml.de/

**Pandas**
    A data analysis toolkit for time series.
    http://pandas.pydata.org/

**PyTables**
    A library for the HDF5 data format.
    http://www.pytables.org

**Numpy**
    A library for n-dimensional arrays, and numerical computations.
    http://www.numpy.org/ 

**Matplotlib**
    A library to create (mainly 2-dimensional) diagrams.
    http://matplotlib.org/

**NLTK**
    A library for processing natural (written) language.
    http://nltk.org/

**PyQt**
    A Python wrapper for the Qt libraries.
    http://www.riverbankcomputing.com/software/pyqt/intro

    Only the GUI parts are dependent on *Qt* and *PyQt*.

**Qt**
    A set of libraries to write graphical applications. Clair uses Qt version *4.x*, it currently uses *Qt 4.7*.
    http://qt-project.org/

    Only the GUI parts are dependent on *Qt* and *PyQt*.

To communicate with Ebay over its API, you need an *Ebay developer key*, which 
can be easily obtained through Ebay's developer website:

    https://go.developer.ebay.com/developers/ebay

There is currently no installation script, the applications must be run in the
source directory (``src/``).

There is example data in the directory ``example-data/``.
Some information from your Ebay developer keys must be filled into the file
``example-data/python-ebay.apikey.example``, and the file must be renamed into 
``example-data/python-ebay.apikey``.

