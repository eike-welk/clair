from django.conf.urls import url, include
from rest_framework import routers

from . import views


# Router for REST API
router = routers.DefaultRouter()
router.register(r'listings', views.ListingViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'prices', views.PriceViewSet)
router.register(r'products-in-listings', views.ProductsInListingViewSet, base_name='ProductsInListing')

urlpatterns = [
    url(r'^$', views.index),
    url(r'^listings/$', views.listings),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
