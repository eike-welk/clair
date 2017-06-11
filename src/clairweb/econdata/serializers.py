from .models import Listing, Product, Price, ProductsInListing
from rest_framework import serializers


class ListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Listing
        fields = (
            'id', 'site', 'id_site', 
            'title', 'description', 'prod_spec', 'condition', 
            'time', 'currency', 'price', 'shipping_price', 'is_real', 'is_sold',
            'location', 'shipping_locations', 'seller', 'buyer', 'item_url', 
            'status', 'listing_type',)

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'important_words', 'categories', 'description',
                  'description_url1', 'description_url2',)

class PriceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Price
        fields = ('id', 'price', 'currency', 'condition', 'time', 'product', 
                  'listing', 'price_type', 'is_sold', 'avg_period', 
                  'avg_num_listings',)

class ProductsInListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProductsInListing
        fields = ('id', 'product', 'listing', 'is_training_data',)
