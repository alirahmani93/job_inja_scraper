from django.db import models


class Job(models.Model):
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    salary = models.CharField(max_length=255)
    publish_time = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
