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
    fixed = models.BooleanField()


class NumberOfTransactions(models.Model):
    amount_equal_transactions = models.IntegerField()
    amount_not_equal_transactions = models.IntegerField()
    amount_not_found_transactions = models.IntegerField()


class NotEqualTransaction(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateField()
    time = models.TimeField()
    name = models.CharField(max_length=200)
    transfer = models.IntegerField()
    fee = models.IntegerField()
    total = models.IntegerField()
    company = models.CharField(max_length=200)
    reference = models.CharField(max_length=200)
    fixed = models.BooleanField()


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
    update_date = models.CharField(max_length=200)
    update_time = models.TimeField()
    reference = models.CharField(max_length=200)
    fixed = models.BooleanField()

class Task(models.Model):
    user = models.CharField(max_length=200)
    ids = models.IntegerField(null=True, blank=True,db_index=True)
    date = models.DateField()
    time = models.TimeField()
    name = models.CharField(max_length=200)
    transfer = models.IntegerField()
    fee = models.IntegerField()
    total = models.IntegerField()
    comment = models.CharField(max_length=400)
    reference = models.CharField(max_length=200)
    status = models.CharField(max_length=200)


# def insert(self):
#     self.save()

