from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

#from .models import Listing, Product, Price
#from .serializers import ListingSerializer, ProductSerializer, PriceSerializer


# Regular Pages ---------------------------------------------------------------
def index(request):
    return HttpResponse("Hello, world. You're at the Collect index.")


## API -------------------------------------------------------------------------
#class ListingViewSet(viewsets.ModelViewSet):
#    """
#    API endpoint that allows listings to be viewed or edited.
#    """
#    queryset = Listing.objects.all().order_by('-time')
#    serializer_class = ListingSerializer
#
#
#class ProductViewSet(viewsets.ModelViewSet):
#    """
#    API endpoint that allows products to be viewed or edited.
#    """
#    queryset = Product.objects.all()
#    serializer_class = ProductSerializer
#
#
#class PriceViewSet(viewsets.ModelViewSet):
#    """
#    API endpoint that allows prices to be viewed or edited.
#    """
#    queryset = Price.objects.all().order_by('-time')
#    serializer_class = PriceSerializer
#
