from django.conf.urls import url, include
from rest_framework import routers

from . import views


# Router for REST API
router = routers.DefaultRouter()
router.register(r'search_tasks', views.SearchTaskViewSet)
router.register(r'events', views.EventViewSet)

urlpatterns = [
    url(r'^$', views.index),
    url(r'^search-tasks/$', views.searchTasks),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
