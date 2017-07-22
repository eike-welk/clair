from django.shortcuts import render
#from django.http import HttpResponse
from rest_framework import viewsets

from .models import Listing, Product, Price, ProductsInListing
from .serializers import ListingSerializer, ProductSerializer, PriceSerializer, \
                         ProductsInListingSerializer


# Regular Pages ---------------------------------------------------------------
def index(request):
    return render(request, 'econdata/index.html', {})

def listings(request):
    return render(request, 'econdata/listings.html', {})

def products(request):
    return render(request, 'econdata/products.html', {})

def product_details(request, product_id):
    print('product_id: ', product_id)
    return render(request, 'econdata/product-details.html', {'product_id': product_id})

def prices(request):
    return render(request, 'econdata/prices.html', {})



# API -------------------------------------------------------------------------
class ListingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows listings to be viewed or edited.
    """
    queryset = Listing.objects.all().order_by('-time')
    serializer_class = ListingSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class PriceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows prices to be viewed or edited.
    """
    queryset = Price.objects.all().order_by('-time')
    serializer_class = PriceSerializer


class ProductsInListingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ProductsInListing records to be viewed or edited.
    """
    serializer_class = ProductsInListingSerializer
    
    def get_queryset(self):
        if 'listing' in self.request.GET:
            # Report the products that are in a specific listing.
            try:
                listing_id = self.request.GET['listing']
#                listing_id = listing_URL.split('/')[-2]
#                print("Listing: " + listing_id)
                listing = Listing.objects.get(id=listing_id)
                qs = ProductsInListing.objects.filter(listing=listing)
                return qs
            except (Listing.DoesNotExist, IndexError):
                return ProductsInListing.objects.none()
        else:
            # Return all records
            return ProductsInListing.objects.all()
