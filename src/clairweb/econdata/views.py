from django.shortcuts import render
from django.forms import ModelForm
#from django.http import HttpResponse
from rest_framework import viewsets

from econdata.models import Listing, Product, Price, ProductsInListing
from econdata.serializers import ListingSerializer, ProductSerializer, PriceSerializer, \
                         ProductsInListingSerializer


# Regular Pages ---------------------------------------------------------------
def index(request):
    return render(request, 'econdata/index.html', {})

def listings(request):
    return render(request, 'econdata/listings.html', {})

def products(request):
    return render(request, 'econdata/products.html', {})

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'categories', 'important_words', 
                  'description_url1', 'description_url2', 'description']
        
def product_details(request, product_id):
    print('product_id: ', product_id)
    
    prod = Product.objects.get(pk=product_id)
    print('product name: ', prod.name)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProductForm(request.POST, instance=prod)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            form.save()

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProductForm(instance=prod)

    return render(request, 'econdata/product-details.html', 
                  {'form': form, 'product_id': product_id})

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
