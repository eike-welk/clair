from django.contrib import admin
from .models import Listing, Product, Price, ProductsInListing


admin.site.register(Listing)
admin.site.register(Product)
admin.site.register(Price)
admin.site.register(ProductsInListing)