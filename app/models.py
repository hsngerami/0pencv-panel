from django.db import models


class Movement(models.Model):
    img = models.ImageField("Image")
    datetime = models.DateTimeField("Date and Time", auto_now_add=True)


class Option(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.BooleanField(default=False)
