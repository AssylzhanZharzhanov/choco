import datetime
import os
from dateutil.parser import parser
from django.db import models
from django.utils import timezone
from django.utils import dates
from bs4 import BeautifulSoup
import re
import codecs
import pandas as pd

class Transaction(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateField()
    name = models.CharField(max_length=200)
    transfer = models.IntegerField()
    fee = models.IntegerField()
    total = models.IntegerField()

def insert(self):
    self.save()

class Payment:
    def __init__(self, name, file):
        self.name = name
        self.file = file
    def getFiles(self):
        return self.file
    def getName(self):
        return  self.name

attachment_dir = '/home/mrx/PycharmProjects/untitled1/docs/'

class KaspiParser:
    def __init__(self, file):
        self.filename = attachment_dir + file

    def getParse(self):
        df = pd.read_excel(self.filename)
        df = pd.DataFrame(df)
        dates = df['Дата транзакции'].dt.date
        ids = df['Номер Транзакции']
        comision = df['Комиссия']
        total = df['Итого к перечислению']
        amount  = df['Сумма']
        datas = []

        for i in range(0, len(dates)):
            data = {
                'id': ids[i],
                'date': dates[i],
                'transfer': amount[i],
                'fee': comision[i],
                'total': total[i],
                'bank': 'kaspi'
            }
            datas.append(data)



class NurbankParser:
    def __init__(self, file):
        self.filename = attachment_dir + file

    def getParse(self):
        df = pd.read_excel(self.filename)
        df = pd.DataFrame(df)
        colnames = df.iloc[2]
        df.columns = colnames
        df = df.drop(df.index[[0, 1, 2]])
        df = df[df['RC_descrip'] == 'Approved or completed successfully']
        df.reset_index(drop=True, inplace=True)

        ids = df['Order ID']
        dates = df['TrDate_Pr.k']
        amount = df['Tran_amoun']
        datas = []

        for i in range(1, len(dates)):
            data = {
                'id': ids[i],
                'date': dates[i],
                'amount': amount[i],
                'total': amount[i],
                'bank': 'Nurbank',
                'fee':0
            }
            datas.append(data)


class KazkomParse:
    def __init__(self, file):
        self.file = file
    def getParse(self):
        attachment_dir = '/home/mrx/PycharmProjects/untitled1/docs/'
        file = '13318-EC27_12_12_merchantrep_17.04.2018-17.04.2018.htm'
        url = attachment_dir + file
        page = codecs.open(url, "r", "utf-8")
        soup = BeautifulSoup(page.read(), "html.parser")
        t = soup.find('table', class_='main-table')
        tr = t.find_all('tr')
        headers = t.find_all('th')
        datas = []
        for i in range(1, len(tr)):
            data = {
                'id': tr[i].find_all('td')[4].text,
                'date': datetime.datetime.date(parser.parse(tr[i].find_all('td')[1].text)),
                'transfer': tr[i].find_all('td')[8].text,
                'fee': tr[i].find_all('td')[9].text,
                'total': tr[i].find_all('td')[10].text,
                'bank':'Kazkom'
            }
            datas.append(data)


class ToursimParser:
    def __init__(self, file):
        self.file = file

    def getParse(self):
        df = pd.read_excel(self.filename)
        df = pd.DataFrame(df)
        cols = df.iloc[0]
        col = []
        for i in range(0, len(cols)):
            col.append(cols[i])
        df.columns = col
        df = df.drop(df.index[[0]])
        df = df[df['Описание результата'] == 'Успешное завершение']
        df.reset_index(drop=True, inplace=True)

        dates = df['Дата']
        amount = df['Сумма платежа']
        ids = df['# Кассовой операции']

        datas = []
        for i in range(0, len(df.index)):
            data = {
                'id': ids[i],
                'date': dates[i],
                'transfer': amount[i],
                'total': amount[i],
                'fee': 0,
                'bank': 'Tourism'
            }
            datas.append(data)

        

#design
#4 excel forms
#json reader