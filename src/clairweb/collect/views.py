from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from .models import SearchTask, Event
from .serializers import SearchTaskSerializer, EventSerializer


# Regular Pages ---------------------------------------------------------------
def index(request):
    return render(request, 'collect/index.html', {})


# API -------------------------------------------------------------------------
class SearchTaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows search tasks to be viewed or edited.
    """
    queryset = SearchTask.objects.all()
    serializer_class = SearchTaskSerializer


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows events to be viewed or edited.
    """
    queryset = Event.objects.all().order_by('-due_time')
    serializer_class = EventSerializer

