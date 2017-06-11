from django.shortcuts import render
#from django.http import HttpResponse
from rest_framework import viewsets

from .models import Listing, Product, Price, ProductsInListing
from .serializers import ListingSerializer, ProductSerializer, PriceSerializer, \
                         ProductsInListingSerializer


# Regular Pages ---------------------------------------------------------------
def index(request):
    return render(request, 'econdata/index.html', {})


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
    API endpoint that allows prices to be viewed or edited.
    """
    queryset = ProductsInListing.objects.all()
    serializer_class = ProductsInListingSerializer

