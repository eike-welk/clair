##############################################
Clair
##############################################

Clair is a project to collect prices on E-Commerce sites, and display them in
graphical form.  It is aimed at used goods, that are not labeled with product
IDs, but that are described with natural languages.  Product recognition is
semi automatic and uses natural language processing. 

Clair is named after Wesley Clair Mitchell, an important US economist, who
mainly worked empirically and collected a big database of prices.  Mitchell
also believed that markets need to be regulated, and was influential in
creating the New Deal.


Development Status
=======================================

The software is currently in an alpha stage. 
There are no usable components, not even crude programs, 
that can be tested without much effort.

Clair is written in Python (version 3) with the Django web framework, the GUI
parts are planned to be written in Javascript with the Angular framework.  It
can currently only communicate with Ebay.


Libraries
=======================================

Clair needs fairly many libraries to function:

**Python Ebaysdk**
    A library to communicate with Ebay over the Internet.
    Ebay seems to treat this library as the official Python API.
    https://github.com/timotheus/ebaysdk-python

**Pandas**
    A data analysis toolkit for time series.
    http://pandas.pydata.org/

**Numpy**
    A library for n-dimensional arrays, and numerical computations.
    http://www.numpy.org/ 

**NLTK**
    A library for processing natural (written) language.
    http://nltk.org/

**Django**
    A framework do create web applications (runs on the server).
    https://www.djangoproject.com/

**Django REST framework**
    An extension for Django to create an API, so that other programs can easily
    communicate with the server.
    http://www.django-rest-framework.org/

**Pytest**
    A test framework that works well for test driven development.
    https://docs.pytest.org/en/latest/

**Pytest-Django**
    An extesion for *Pytest* to work with Django.
    https://pytest-django.readthedocs.io/en/latest/

**AngularJS**
    A framework for complex applications in Javascript, that run in the
    browser.

**Bootstrap**
    A CSS and Javascript framework for styling applications.


Installation and Usage
=======================================

There is currently no installation script. But there is ``requirements.txt``,
that lists all Python libraries, that need to be installed.

You can use the following commands (preferably in a ``virtualenv``) to: Clone
the repository, install the necessary libraries, set up the server, and run
it::

    git clone https://github.com/eike-welk/clair.git
    cd clair/
    pip install -r requirements.txt

    cd src/clairweb/
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

The applications is run in the source directory (``src/clairweb``).
Be sure to use Python version 3, which is named ``python3`` in
many Linux distributions. (But it is named ``python`` in ``virtualenv``.)

To communicate with Ebay over its API, you need an *Ebay developer key*, which 
can be easily obtained through Ebay's developer website:

    https://go.developer.ebay.com/developers/ebay

Some information from your Ebay developer keys must be filled into the file
``src/clairweb/ebay-sdk.apikey.example``. The file must then be renamed into 
``src/clairweb/ebay-sdk.apikey``.

There is example data in the directory ``example-data/``.

