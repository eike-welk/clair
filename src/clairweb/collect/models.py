from django.db import models

import econdata.models


class SearchTask(models.Model):
    "Tasks to search for a certain product.",
    id = models.AutoField(
            "Internal unique ID of each search task.",
            primary_key=True)
    recurrence = models.DurationField(
            "How frequently should the task be executed.",)
    server = models.CharField(
            "The server where products should be searched.",
            max_length=64,)
    product = models.ForeignKey(
            econdata.models.Product,
            verbose_name="The product which is searched by this task.",
            related_name="related_search_task",
            on_delete=models.CASCADE, blank=True, null=True,)
    query_string = models.CharField(
            "The query string that is given to the server. "
            "If the string is blank, it is constructed from the product.",
            max_length=128, blank=True, default='',)
    n_listings = models.IntegerField(
            "Number of listings that should be returned by the server.",)
    price_min = models.FloatField(
            "Minimum price for searched items.",
            blank=True, null=True,)
    price_max = models.FloatField(
            "Maximum price for searched items.",
            blank=True, null=True,)
    currency = models.CharField(
            "Currency of the prices.",
            max_length=3, blank=True, default='')

    def __str__(self):
        return "{id}, {prod}, {rec}".format(
                id=self.id, 
                prod=self.product.name if self.product is not None else self.query_string, 
                rec=self.recurrence)


class ListingFoundBy(models.Model):
    "Remember which ``SearchTask`` found which ``Listing``"
    id = models.AutoField(
            "Internal unique ID.",
            primary_key=True)
    task = models.IntegerField(
            'ID of the task that found the listing',)
    listing = models.CharField(
            'ID of the listing that was found by the task',
            max_length=128)

#     task = models.ForeignKey(
#             SearchTask,
#             verbose_name='The task that found the listing',
#             on_delete=models.CASCADE, blank=True, null=True,)
#     listing = models.ForeignKey(
#             econdata.models.Listing,
#             verbose_name='The listing that was found by the task',
#             on_delete=models.CASCADE, blank=True, null=True,)

    def __str__(self):
        return "id={id}, task={task}, listing={listing}".format(
                id=self.id, task=self.task, listing=self.listing)


class Event(models.Model):
    "Schedule search tasks and updates of listings."
    id = models.AutoField(
            "Internal unique ID of each scheduled event.",
            primary_key=True)
    due_time = models.DateTimeField(
            "Time when event should be executed.",)
    listing = models.ForeignKey(
            econdata.models.Listing,
            verbose_name="The listing that should be updated.",
            on_delete=models.CASCADE, blank=True, null=True,)
    search_task = models.ForeignKey(
            SearchTask,
            verbose_name="The search task that should be executed.",
            on_delete=models.CASCADE, blank=True, null=True,)

    def __str__(self):
        return "{id}, {due}".format(
                id=self.id, due=self.due_time,)

