from django.db import models

class Listing(models.Model):
    """
    2D Table of listings
    Each row represents a listing on an e-commerce site.
    """
    format_version = "1.0"

    # IDs ---------------------------------------------------------------------
    id = models.CharField(
            "Internal unique ID of each listing. Approximate pattern: "
            "date-site-id_site, for example: 2017-01-01-Ebay-123478901234567",
            max_length=64, primary_key=True)
    site = models.CharField(
            "String to identify the remote site. For example 'Ebay'.", 
            max_length=8)
    id_site = models.CharField(
            "ID of listing on the remote site.",
            max_length=44)
    # Product description -----------------------------------------------------
    title = models.CharField(
            "Short description of listing.",
            max_length=128),
    description = models.CharField(
            "Long description of listing.",
            max_length=1024*8, blank=True, default='')
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
    item_url = models.CharField(
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

