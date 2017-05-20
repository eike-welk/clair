###############################################################################
#    Clair - Project to discover prices on e-commerce sites.                  #
#                                                                             #
#    Copyright (C) 2017 by Eike Welk                                          #
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
Models (database tables) for economic data.
For example: Listings, products, prices, and their relations.
"""
from django.db import models


class Listing(models.Model):
    """
    2D Table of listings
    Each row represents a listing on an e-commerce site.
    """
    # IDs ---------------------------------------------------------------------
    id = models.CharField(
            "Internal unique ID of each listing. Approximate pattern: "
            "date-site-id_site, for example: 2017-01-01-Ebay-123478901234567",
            max_length=64, primary_key=True)
    site = models.CharField(
            "String to identify the remote site. For example 'Ebay'.", 
            max_length=8)
    id_site = models.CharField(
            "the listing's ID on the remote site.",
            max_length=44)
    # Product description -----------------------------------------------------
    title = models.CharField(
            "Short description of the listing.",
            max_length=128)
    description = models.TextField(
            "Long description of the listing.",
            blank=True, default='')
    prod_spec = models.CharField(
            "Product specific name value pairs (dict), in JSON. For example: "
            "``{'megapixel': '12'}``. The ``ItemSpecifics`` on Ebay.",
            max_length=256, blank=True, default='')
    CONDITION_CHOICES = (
            ('new',             'New'),
            ('new-defects',     'New with defects'),
            ('refurbished',     'Refurbished'),
            ('used',            'Used'),
            ('used-very-good',  'Used very good'),
            ('used-good',       'Used good'),
            ('used-acceptable', 'Used acceptable'),
            ('not-working',     'Not working'),     )
    condition = models.CharField(
            "Condition of the sold item(s):",
            max_length=16, choices=CONDITION_CHOICES, blank=True, default='')
    # Price -------------------------------------------------------------------
    time = models.DateTimeField(
            "Time when price is/was valid. End time in case of auctions.",
            blank=True, null=True, default=None)
    currency = models.CharField(
            "Currency for price EUR, USD, ...",
            max_length=3, blank=True, default='')
    price = models.FloatField(
            "Price of listing (all items together).",
            blank=True, null=True, default=None)
    shipping_price = models.FloatField(
            "Shipping cost",
            blank=True, null=True, default=None)
    is_real = models.NullBooleanField(
            "If True: One could really buy the item for this price. "
            "This is not a temporary price from an ongoing auction.",
            blank=True, null=True, default=None)
    is_sold = models.NullBooleanField(
            "Successful sale if ``True``.",
            blank=True, null=True, default=None)
    # Listing Data ------------------------------------------------------------
    location = models.CharField(
            "Location of item (pre sale)",
            max_length=64, blank=True, default='')
    shipping_locations = models.CharField(
            "Locations to where the item(s) can be shipped.",
            max_length=64, blank=True, default='')
    seller = models.CharField(
            "User name of seller.",
            max_length=64, blank=True, default='')
    buyer = models.CharField(
            "User name of buyer.",
            max_length=64, blank=True, default='')
    item_url = models.URLField(
            "Link to web representation of listing.",
            max_length=256, blank=True, default='')
    # Status values -----------------------------------------------------------
    STATUS_CHOICES = (
             ('active', 'Active'),
             ('canceled', 'Canceled'),
             ('ended', 'Ended'),  )
    status = models.CharField(
            "State of the listing: active, canceled, ended",
            max_length=8, choices=STATUS_CHOICES, blank=True, default='')
    LISTING_TYPE_CHOICES = (
             ('auction', 'Auction'),
             ('classified', 'Classified'),
             ('fixed-price', 'Fixed price'),    )
    listing_type = models.CharField(
            "Type of the listing: auction, classified, fixed-price",
            max_length=16, choices=LISTING_TYPE_CHOICES, blank=True, default='')

    def __str__(self):
        return self.id + ', ' + self.title


class Product(models.Model):
    """
    Description of a Product.
    """
    id = models.CharField(
            "Internal unique ID of each product.",
            max_length=64, primary_key=True)
    name = models.CharField(
            "Product name. A single line of text.",
            max_length=256, default='')
    important_words = models.CharField(
            "Important words for the text recognition algorithms.",
            max_length=256, blank=True, default='')
    categories = models.CharField(
            "Categories for grouping products. "
            "Comma separated list of words (with dots in them).",
            max_length=256, blank=True, default='')
    description = models.TextField(
            "Description of the product. Any text.",
            blank=True, default='')
    description_url1 = models.URLField(
            "Link to website that describes the product (1).",
            max_length=256, blank=True, default='')
    description_url2 = models.URLField(
            "Link to website that describes the product (2).",
            max_length=256, blank=True, default='')

    def __str__(self):
        return self.id + ', ' + self.name


class Price(models.Model):
    """
    Price of a product at a certain point in time.
    """
    id = models.AutoField(
            "Internal unique ID of each price.",
            primary_key=True)
    price = models.FloatField(
            "The numeric value of the price.")
    currency = models.CharField(
            "The currency of the price. For example: 'EUR', 'USD'",
            max_length=3)
    condition = models.FloatField(
            "Multiplier for condition. \n"
            "1.0: new/perfect, 0.7: used, 0.0: worthless. ")
    time = models.DateTimeField(
            "Time and date at which the price was payed.")
    product = models.ForeignKey(
            Product,
            verbose_name="ID of product for which the price is recorded.",
            related_name='related_price_record',
            on_delete=models.CASCADE, blank=True, null=True,)
    listing = models.ForeignKey(
            Listing,
            verbose_name="ID of listing from which the price is taken.",
            related_name='related_price_record',
            on_delete=models.CASCADE, blank=True, null=True,)
    PRICE_TYPE_CHOICES = (
            ('observed',  'There was a listing with only one product, '
                          'and this was the price.'),
            ('estimated', 'The price was estimated by some algorithm.'),
            ('average',   'This is an average price.'),
            ('guessed',   'A human has guessed the price.'),   )
    price_type = models.CharField(
           "Type of the price record.",
            max_length=16, choices=PRICE_TYPE_CHOICES)
    is_sold = models.NullBooleanField(
            "Successful sale if ``True``.",
            blank=True, null=True,)
    AVG_PERIOD_CHOICES = (
            ('none',  'No averaging was done.'),
            ('day',   'Average over one day.'),
            ('week',  'Average over one week.'),
            ('month', 'Average over one month.'),   )
    avg_period = models.CharField(
            "Time span for taking average. Can be 'day', 'week', 'month'.",
            max_length=16, choices=AVG_PERIOD_CHOICES)
    avg_num_listings = models.IntegerField(
            "Number of listings used in computation of average.")

    def __str__(self):
        return self.id + ', ' + self.price + ' ' + self.currency + ', ' + self.time

