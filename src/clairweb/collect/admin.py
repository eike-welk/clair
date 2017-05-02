from django.contrib import admin

from .models import SearchTask, Event


admin.site.register(SearchTask)
admin.site.register(Event)
