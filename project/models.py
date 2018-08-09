import datetime
import os
# from dateutil.parser import parser
from django.db import models
from django.utils import timezone
from django.utils import dates
from bs4 import BeautifulSoup
import re
import codecs
import datetime
from dateutil import parser
import re
import codecs
import pandas as pd
import numpy as np

class Transaction(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateField()
    time = models.TimeField()
    name = models.CharField(max_length=200)
    transfer = models.IntegerField()
    fee = models.IntegerField()
    total = models.IntegerField()
    company = models.CharField(max_length=200)
    updated = models.BooleanField()
    update_time = models.TimeField()
    reference = models.CharField(max_length=200)


class UpdatedTransaction(models.Model):
    ids = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()
    name = models.CharField(max_length=200)
    transfer = models.IntegerField()
    fee = models.IntegerField()
    total = models.IntegerField()
    company = models.CharField(max_length=200)
    # updated = models.BooleanField()
    update_time = models.TimeField()
    reference = models.CharField(max_length=200)

class Task(models.Model):
    user = models.CharField(max_length=200)
    data = UpdatedTransaction()
# def insert(self):
#     self.save()

