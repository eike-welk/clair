##########
Data Types
##########

Online Price Discovery Project

These are the main data types that are used by the algorithms. If the data is
stored as XML on disk, a version field is added to the data. For
important data (listings, price points) algorithms to read each version are
kept working, so that historical data can be used without conversion.


Get Information over Internet
=============================

Configuration information for algorithms that download listings from servers and return them.

SearchTask
----------

A job for searching for a product or a set of products on the Internet.

* id
* due_time
* recurrence pattern
* server
    Maybe call it site?
* queries : list of strings
    Servers usually have a query language. This is a list of queries in this
    language.
* expected_products : list of ProductDescription 
    Help for the UI for manually assigning products to listings. 
* parameters for automatic product detection and machine learning.

UpdateTask
----------

Update the status of listings.

* id
* due_time
* server
* listings


Product
=======

A specific product.

ProductDescription
------------------

* id : str
    Unique identification string for a product. Must not contain spaces, to
    avoid confusion with names.  Must not be changed ever.
* name : str
    Name of the product. Should/must be unique too. Can be changed.
* important_words : list[str]
    Additional words that are important in conjunction with this product. These
    words are added to the vocabulary of the learning algorithm, but they do
    not need to be positive terms. The product name is also added to the
    vocabulary.
* description : str
* categories : list[str]
* product specific fields

DetectedProduct
---------------
* id
* name
* quantity
* condition : float 1..0 (1=new, 0=worthless, nan=unknown)
* recognition_quality
    Measure of the certainty that the automatic recognition algorithm has
    correctly identified the product. 

* estimated_price : float
* currency : string


Listing
=======

A single offer that a buyer can purchase. It might contain a single item or
multiple items. It may have a fixed price or be an auction.

Listing
-------

* id
    Internal unique ID of each listing.

* training_sample : bool
* expected_products : list of ProductDescription / product IDs
* query_string 

* title
* description
* products : list of DetectedProduct
* price
* shipping
* type : auction, fixed_price
* time_finished : date_time 
* condition : float 1..0 (1=new, 0=worthless, nan=unknown)
* location

* server
* id_server
    ID of the item on the server.
* server_xml
* data_directory
* url_webui
* server specific fields


Price
=====

A price of a product at a certain time. The customer buys a certain listing,
and the price for each product is deduced from the listing's price. If the
listing contains only one product this is easy. If there are multiple products
in the listing, an algorithm must estimate the price of each product. The
algorithm probably needs to know previous prices of each product.  

Price
-----

* product_name
* product_state : new, like_new, used, degraded, broken, unknown
* price
* currency
* time : date_time
* server
* location
* success : successful, unsuccessful, unknown
    Is this the price of a successful sale?
* listing
    Link to listing from which price was deduced
* product specific fields


