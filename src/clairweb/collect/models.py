from django.db import models


class SearchTask(models.Model):
    "Tasks to search for a certain product.",
    # IDs ---------------------------------------------------------------------
    id = models.AutoField(
            "Internal unique ID of each search task.",
            primary_key=True)
