from .models import SearchTask, Event
from rest_framework import serializers


class SearchTaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SearchTask
        fields = (
            'id', 'recurrence', 'server', 'product', 'query_string', 
            'n_listings', 'price_min', 'price_max', 'currency',)

class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'due_time', 'listing', 'search_task',)

