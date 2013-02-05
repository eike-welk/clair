#########
Libraries
#########

Online Price Discovery Project


Ebay API
========

https://www.x.com/developers/ebay

Generally, using the API requires registration with Ebay. A programmer receives a set of secret keys, that she must not share. Programs that are released to users must be checked by Ebay. Checked programs are called `compatible programs`. Access to the bidding API requires special permission from Ebay.

There is a call limit for programs. For programs that have not been checked it is fairly restrictive (5000 calls / day). For compatible programs it is much higher (1.5 million calls / day).

    https://www.x.com/developers/ebay/ebay-api-call-limits

Ebay seems not to like programs that gather statistical information. But gathering statistical information seems to be generally allowed in the license for Ebay's API. In the ``API License Agreement`` only some specific statistics are excluded, that reveal information about the performance of Ebay as a business. However it is stated in the website, that compatible programs should not gather statistical information though the API. 

    https://www.x.com/developers/ebay/support/certification
    http://developer.ebay.com/join/licenses/individual/


The API is available in different programming languages:

Java
----

https://www.x.com/developers/ebay/documentation-tools/sdks/java
Common Development and Distribution License (CDDL)

Python
------

Python-Ebay                         **Dependency**
..................................................

Seems to be the most popular Ebay library for Python. Classical library, not
object oriented, with global configuration. Code looks a bit messy.
Not much documentation, but tests and examples.

Apache License, Version 2.0

https://github.com/roopeshvaddepally/python-ebay

Ebaysdk-Python
..............

Apache License, Version 2.0

https://github.com/timotheus/ebaysdk-python

Ebaysuds
........

New library, where the Python glue code is automatically generated from a
machine readable description (in XML). This mechanism is called SOAP.
Object oriented, no central configuration. Library is very small, and a thin
wrapper on top of the ``suds`` library. Currently no documentation.

LGPL v3

https://github.com/anentropic/ebaysuds 


ql.io
-----

ql.io is a declarative language for querying Ebay and possibly other web
services. Using it reduces the size of the program's source code, and the
numbers of calls to the Ebay API.

Apache License, Version 2.0

https://www.x.com/developers/ebay/documentation-tools/ql.io


JavaScript
----------

PHP
---

Proprietary Languages
---------------------

Flash, .Net languages


Amazon API
==========

Amazon has an API with fairly restrictive usage terms.

https://affiliate-program.amazon.com/gp/advertising/api/detail/main.html


Hood API
========

There seems to be an API but nearly no information about it is published.


Machine Learning Libraries
==========================

Slides and video of tutorial talk on text classification and machine learning with Python:
http://www.slideshare.net/ogrisel/statistical-machine-learning-for-text-classification-with-scikitlearn-and-nltk

Tips to improve accuracy and performance of a text classification algorithm:
http://thinknook.com/10-ways-to-improve-your-classification-algorithm-performance-2013-01-21/


Scikit-Learn
------------

Machine learning library. Library for Python, implementation probably partially
in compiled languages, associated with Numpy and Scipy.

http://scikit-learn.org/stable/

How to work with text data in Scikit-Learn:
http://scikit-learn.github.com/scikit-learn-tutorial/working_with_text_data.html

Choose the right algorithm in Scikit-Learn:
http://peekaboo-vision.blogspot.de/2013/01/machine-learning-cheat-sheet-for-scikit.html


NLTK - Natural Language Toolkit
-------------------------------

Specialized library for processing text in natural languages. Library for
Python, implementation probably partially in compiled languages.

http://nltk.org/

The library is accompanied by an online book. Chapter 6 is about machine learning:
http://nltk.org/book/

Pattern
-------

Python, supposedly contains out-of-the-box solutions, seems to include parser for German.

http://www.clips.ua.ac.be/pages/pattern


Gensim
------

Python, specialized for natural language processing, maybe only for unsupervised learning.

http://radimrehurek.com/gensim/


Orange
------

Python, mainly for biologists, but with components for text mining. Supposedly scales well.

http://orange.biolab.si/


Shogun
------

Large scale machine learning toolbox with bindings for Python, Java, among others.
Implementation seems to be in C++, with some Python on the top level.

http://www.shogun-toolbox.org/


Additional Libraries
====================


Pandas - Data analysis toolkit for time series
----------------------------------------------

Python. Pandas is a data analysis toolkit for time series.
It stores values together with labels, which can be date-time or anything else. 
Data can be indexed by label / time interval.
Special plotting algorithms. Stores data in HDF5 format.

http://pandas.pydata.org/pandas-docs/stable/index.html


PyTables - HDF5 library
-----------------------

Python. PyTables is a library to store data in the HDF5 format. It can manage
hierarchical datasets and is designed to cope with extremely large amounts of
data. Used by Pandas.

http://www.pytables.org


Requests - HTTP for Humans          **Dependency**
--------------------------------------------------

Python. Simple HTTP library. Used by: Python-Ebay library.

http://docs.python-requests.org/en/latest/


LXML - XML parsing library          **Dependency**
--------------------------------------------------

Python. Fast XML parsing library, that uses a very similar API as ElementTree.
Used by: Python-Ebay library.

http://lxml.de/


Theano - Speed up Numerical Computations
----------------------------------------

Python library to speed up numerical computations, and to do computations on
the GPU. Can also do automatic differentiation.

http://deeplearning.net/software/theano/
