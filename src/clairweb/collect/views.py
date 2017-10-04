from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from .models import SearchTask, Event
from .serializers import SearchTaskSerializer, EventSerializer


# Regular Pages ---------------------------------------------------------------
def index(request):
    return render(request, 'collect/index.html', {})

def searchTasks(request):
    return render(request, 'collect/search-tasks.html', {})

def search_task_details(request, search_task_id):
    print('search-task_id: ', search_task_id)
    task = SearchTask.objects.get(pk=search_task_id)

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

