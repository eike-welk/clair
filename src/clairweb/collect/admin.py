from django.contrib import admin

from .models import SearchTask, Event, ListingFoundBy


admin.site.register(SearchTask)
admin.site.register(ListingFoundBy)
admin.site.register(Event)
