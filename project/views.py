import datetime
import json
from dateutil import parser
from collections import namedtuple

from django.contrib import auth
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from project.forms import PostForm
from .models import Transaction
from project.forms import UpdateForm
from project.GmailParser import Parser
import datetime
import os
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
# from project.models import Payment,KaspiParser,NurbankParser,KazkomParser,ToursimParser
import logging
from project.models import UpdatedTransaction
from actions.utils import create_action
logger = logging.getLogger(__name__)
# from project.models import Data

# user registration
# time done
# add time and compare done
# buttons done
# logs
# filters

#-------------------------------------------Parsers--------------------------------------------------------
class Data:
    def __init__(self, id, date, time, reference, transfer, fee, total, bank):
        self.id = id
        self.date = date
        self.time=time
        self.reference = reference
        self.transfer = transfer
        self.fee = fee
        self.total = total
        self.bank = bank

        def getArr(self):
            data = {
                'id': self.id,
                'date':self.date,
                'time': self.time,
                'transfer': self.transfer,
                'reference': self.reference,
                'fee':self.fee,
                'total': self.total,
                'bank':self.bank
            }
            return data

class Payment:
    def __init__(self, name, file):
        self.name = name
        self.file = file
    def getFiles(self):
        return self.file
    def getName(self):
        return  self.name

attachment_dir = '/home/mrx/Documents/choko-master/docs/'

def insertData(datas, request):
    for i in range(0, len(datas)):
        transactions = Transaction.objects.filter(id=datas[i]['id'])
        if(len(transactions) == 0):
            transaction = Transaction(id = datas[i]['id'], date = datas[i]['date'], time = datas[i]['time'], name = datas[i]['bank'], transfer=datas[i]['transfer'],
                                  fee=datas[i]['fee'], total=datas[i]['total'], updated=False, update_time=datas[i]['time'], company="Chocotravel/Aviata",
                                  reference=datas[i]['reference'])
            transaction.save()
            create_action(request.user, 'Inserted new transaction which id: %s' %(datas[i]['id']), (datas[i]['id']))
            updated = UpdatedTransaction(ids=datas[i]['id'], date=datas[i]['date'], time=datas[i]['time'],
                                         name=datas[i]['bank'], transfer=datas[i]['transfer'],
                                         fee=datas[i]['fee'], total=datas[i]['total'], update_time=datas[i]['time'],
                                         company="Chocotravel/Aviata",
                                         reference=datas[i]['reference'])
            updated.save()
        else:
             if datas[i]['time'] > transactions.get(date=datas[i]['date']).time and datas[i]['date'] >= transactions.get(date=datas[i]['date']).date :
                 Transaction.objects.filter(id = datas[i]['id'],date = datas[i]['date']).update(time = datas[i]['time'], transfer=datas[i]['transfer'], fee=datas[i]['fee'], total=datas[i]['total'], updated=True, update_time=datas[i]['time'], company="Chocotravel/Aviata",reference=datas[i]['reference'])
                 updated = UpdatedTransaction(ids = datas[i]['id'],date = datas[i]['date'],time = datas[i]['time'], name = datas[i]['bank'], transfer=datas[i]['transfer'],
                                  fee=datas[i]['fee'], total=datas[i]['total'], update_time=datas[i]['time'], company="Chocotravel/Aviata",
                                  reference=datas[i]['reference'])
                 create_action(request.user, 'While inserting a data by id %s was updated' %(datas[i]['id']), (datas[i]['id']))
                 updated.save()
                 # write to log if updated
            # print(transactions.get(date=datas[i]['date']).name)
        #else comparing by dates and total sum are they equal
        #add company

class KaspiParser:
    def __init__(self, file, request):
        self.filename = attachment_dir + file
        self.request = request

    def getParse(self):
        df = pd.read_excel(self.filename)
        df = pd.DataFrame(df)
        dates = df['Дата транзакции'].dt.date + datetime.timedelta(days=1)
        time = df['Дата транзакции'].dt.time
        reference = df['Номер Транзакции']
        ids = df['Номер бронирования']
        comision = df['Комиссия']
        total = df['Итого к перечислению']
        amount  = df['Сумма']
        datas = []

        for i in range(0, len(dates)):
            data = {
                'id': ids[i],
                'date': dates[i],
                'time': time[i],
                'reference':reference[i],
                'transfer': amount[i],
                'fee': comision[i],
                'total': total[i],
                'bank': 'Kaspi'
            }
            datas.append(data)
        insertData(datas,self.request)

class NurbankParser:
    def __init__(self, file,request):
        self.filename = attachment_dir + file
        self.request = request

    def getParse(self):
        df = pd.read_excel(self.filename)
        df = pd.DataFrame(df)
        colnames = df.iloc[2]
        df.columns = colnames
        df = df.drop(df.index[[0, 1, 2]])
        # df = df[df['RC_descrip'] == 'Approved or completed successfully']
        df['Tran_amoun'] = np.where(df['Resp'] == 'Decline', 0, df['Tran_amoun'])
        df.reset_index(drop=True, inplace=True)

        ids = df['Order ID']
        dates = df['AlmDate'].dt.date
        reference = df['RRN(Pr.kz)']
        time = df['AlmDate'].dt.time
        amount = df['Tran_amoun']
        datas = []

        for i in range(0, len(dates)):
            data = {
                'id': ids[i],
                'date': dates[i],
                'time':time[i],
                'reference' : reference[i],
                'transfer': amount[i],
                'total': amount[i],
                'bank': 'Processing',
                'fee':0
            }
            datas.append(data)
        insertData(datas,self.request)

class KazkomParser:
    def __init__(self, file,request):
        self.file = file
        self.request = request

    def getParse(self):
        url = attachment_dir + self.file
        page = codecs.open(url, "r", "utf-8")
        soup = BeautifulSoup(page.read(), "html.parser")
        t = soup.find('table', class_='main-table')
        tr = t.find_all('tr')
        headers = t.find_all('th')
        datas = []
        for i in range(1, len(tr)):
            data = {
                'id': int(tr[i].find_all('td')[4].text),
                'date': datetime.datetime.date(parser.parse(tr[i].find_all('td')[1].text)),
                'time':datetime.datetime.time(parser.parse(tr[i].find_all('td')[1].text)),
                'reference': tr[i].find_all('td')[7].text,
                'transfer': float(tr[i].find_all('td')[8].text),
                'fee': float(tr[i].find_all('td')[9].text),
                'total': float(tr[i].find_all('td')[10].text),
                'bank':'Kazkom'
            }
            datas.append(data)
        insertData(datas,self.request)

class ToursimParser:
    def __init__(self, file,request):
        self.file = attachment_dir + file
        self.request = request

    def getParse(self):
        df = pd.read_excel(self.file)
        df = pd.DataFrame(df)
        cols = df.iloc[0]
        col = []
        for i in range(0, len(cols)):
            col.append(cols[i])
        df.columns = col
        df = df.drop(df.index[[0]])
        # df = df[df['Описание результата'] == 'Успешное завершение']
        df.reset_index(drop=True, inplace=True)

        dates = pd.to_datetime(df['Дата'],errors='coerce').dt.date
        time = pd.to_datetime(df['Дата'],errors='coerce').dt.time
        amount = df['Сумма платежа']
        df['# Операции в биллинге'] = np.where(df['# Операции в биллинге'].isna(), -1, df['# Операции в биллинге'])
        # print(df['# Операции в биллинге'])
        ids = df['# Операции в биллинге']
        reference = df['# Кассовой операции']
        datas = []
        for i in range(0, len(ids)-1):
            data = {
                'id': ids[i],
                'date': dates[i],
                'time': time[i],
                'reference':reference[i],
                'transfer': amount[i],
                'total': amount[i],
                'fee': 0,
                'bank': 'Tourism'
            }
            datas.append(data)
        insertData(datas,self.request)

#-------------------------------------------------------------------------------------------------------------------

ids = [1,2,3,4]
names = ['kaspi', 'processing', 'tourism', 'kazkom']

class FormView(TemplateView):
    template_name = 'project/transaction_list.html'

    simplelist = []
    for i in range(0, len(names)):
        files = []
        th = Parser(names[i], files)
        th.start()
        file = th.file
        x = Payment(names[i], file)
        simplelist.append(x)

    def get(self, request):
        form = PostForm()
        direction = "ChocoToPayment"
        return render(request, self.template_name, {'form':form, 'direction':direction, 'username': auth.get_user(request).username})

    def post(self,request):

        submitbutton = request.POST.get("submit")
        fixbutton = request.POST.get("fix")
        name = request.POST.get("name")
        request.session["bank"] = name
        start = request.POST.get("start_date")
        end = request.POST.get("end_date")
        direction = request.POST.get("direction")
        filename = '/home/mrx/Documents/choko-master/docs/api.json'
        myfile = open(filename, 'r', encoding='Latin-1')
        json_data = json.load(myfile)
  #------------------------------------fix-------------------------------
        if not request.user.is_authenticated:
            args = {'message': "Please enter your username and password! "}
            return render(request, 'login.html', args)
        else:
            if fixbutton == 'fix':
                Fix = []
                notFix = []
                for i in range(0, len(fix_datas)):
                    if(i%2 == 0):
                        notFix.append(fix_datas[i])
                    else :
                        Fix.append(fix_datas[i])

                for i in range(0, len(Fix)):
                    if(Fix[i].transfer != notFix[i].transfer):
                        for x in json_data:
                            if x['order_id'] == Fix[i].id and x['payment_reference'] == Fix[i].reference:
                                x['payment_amount'] = notFix[i].transfer
                                transactions = Transaction.objects.get(id = Fix[i].id, reference=Fix[i].reference)
                                updateTransaction = UpdatedTransaction(ids = transactions.id, date = transactions.date, time = transactions.time, name = transactions.name, transfer=transactions.transfer,
                                      fee=transactions.fee, total=transactions.total, update_time=datetime.datetime.time(datetime.datetime.now()), company="Chocotravel/Aviata",
                                      reference=transactions.reference)
                                updateTransaction.save()
                                print(request.session["bank"])
                                create_action(request.user, "Fixed %s datas by id: %s" %(transactions.name, transactions.id), transactions.id)
                                #insert updated datas

                del request.session['bank']
                with open('/home/mrx/Documents/choko-master/docs/api.json', 'w') as outfile:
                    json.dump(json_data, outfile, indent=2)
                        #find a transfer by id and reference and fix it in json

                direction = "ChocoToPayment"
                return render(request, self.template_name, {'direction': direction, 'username': auth.get_user(request).username})
      # ------------------------------------------------------------------------------------------------------------------------
            if (submitbutton == 'search'):
               if direction == "ChocoToPayment":
                    equal = []
                    notequal = []
                    notfound = []

                    equal_total = Data(' ', ' ', ' ', ' ', 0, 0, 0, ' ')
                    notequal_total = Data(' ', ' ', ' ', ' ', 0, 0, 0, ' ')

                    for data in json_data:
                        if data['payment_code'] == name.upper():
                            tr = Transaction.objects.filter(id = data['order_id'],date__range=[start, end])
                            if len(tr) > 0:
                                for i in tr:
                                    if i.transfer == data['payment_amount'] and i.reference == data['payment_reference']:
                                        a = Data(i.id, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name)
                                        b = Data(data['order_id'], datetime.datetime.date(parser.parse(data['date_created'])),
                                                 datetime.datetime.time(parser.parse(data['date_created'])),
                                                 data['payment_reference'], data['payment_amount'], 0, data['payment_amount'],
                                                 'Chocotravel/Aviata')
                                        equal.append(a)
                                        equal.append(b)
                                        equal_total.transfer = float(equal_total.transfer) + float(a.transfer)
                                        equal_total.fee = float(equal_total.fee) + float(a.fee)
                                        equal_total.total = float(equal_total.total) + float(a.total)
                                    elif i.transfer != data['payment_amount']  and i.reference == data['payment_reference']:

                                        a = Data(i.id, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name)
                                        b = Data(data['order_id'],
                                                 datetime.datetime.date(parser.parse(data['date_created'])),
                                                 datetime.datetime.time(parser.parse(data['date_created'])),
                                                 data['payment_reference'],
                                                 data['payment_amount'], 0, data['payment_amount'],
                                                 'Chocotravel/Aviata')
                                        notequal.append(a)
                                        notequal.append(b)
                                        notequal_total.transfer = notequal_total.transfer + a.transfer
                                        notequal_total.fee = notequal_total.fee + a.fee
                                        notequal_total.total = notequal_total.total + a.total
                            else:
                                notfound.append(Data(data['order_id'], datetime.datetime.date(parser.parse(data['date_created'])),
                                                     datetime.datetime.time(parser.parse(data['date_created'])), data['payment_reference'],
                                                     data['payment_amount'], 0, data['payment_amount'], 'Chocotravel/Aviata'))
                    global  fix_datas
                    fix_datas = notequal

                    create_action(request.user, 'Searched transactions between %s and %s in %s' % (start, end, name), 0)
                    args = {'name': name, 'equal': equal, 'notequal': notequal, 'notfound': notfound,
                            'equal_total': equal_total, 'notequal_total': notequal_total,'direction':direction, 'username': auth.get_user(request).username}
                    return render(request, self.template_name, args)
        #-----------------------------------------------------------------------------------------------------------
               if direction == "PaymentToChoco":
                    ps_equal = []
                    ps_notequal = []
                    ps_notfound = []
                    ps_equal_total = Data(' ', ' ', ' ', ' ', 0, 0, 0, ' ')
                    ps_notequal_total =  Data(' ', ' ', ' ', ' ', 0, 0, 0, ' ')
                    transactions = Transaction.objects.filter(name__contains=name, date__range=[start, end])
                    # print(len(transactions))
                    for i in transactions:
                        data = [x for x in json_data if x['order_id'] == i.id and x['payment_code'] == name.upper()]
                        if len(data) > 0:
                            if(data[0]['payment_amount'] == i.transfer and  i.reference == data[0]['payment_reference']):
                                a = Data(i.id, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name)
                                b = Data(data[0]['order_id'], datetime.datetime.date(parser.parse(data[0]['date_created'])),
                                         datetime.datetime.time(parser.parse(data[0]['date_created'])),data[0]['payment_reference'],
                                         data[0]['payment_amount'], 0, data[0]['payment_amount'], 'Chocotravel/Aviata')
                                ps_equal.append(a)
                                ps_equal.append(b)
                                ps_equal_total.transfer = ps_equal_total.transfer + a.transfer
                                ps_equal_total.fee = ps_equal_total.fee + a.fee
                                ps_equal_total.total = ps_equal_total.total + a.total
                            elif data[0]['payment_amount'] != i.transfer  and i.reference == data[0]['payment_referencex']:
                                a = Data(i.id, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name)
                                b = Data(data[0]['order_id'], datetime.datetime.date(parser.parse(data[0]['date_created'])),
                                         datetime.datetime.time(parser.parse(data[0]['date_created'])),
                                         data[0]['payment_reference'],
                                         data[0]['payment_amount'], 0, data[0]['payment_amount'], 'Chocotravel/Aviata')
                                ps_notequal.append(a)
                                ps_notequal.append(b)
                                ps_notequal_total.transfer = ps_notequal_total.transfer + a.transfer
                                ps_notequal_total.fee = ps_notequal_total.fee + a.fee
                                ps_notequal_total.total = ps_notequal_total.total + a.total
                        else:
                            ps_notfound.append(Data(i.id, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name))

                    create_action(request.user, 'Searched transactions between %s and %s' % (start, end),0  )
                    args = {'name': name, 'ps_equal': ps_equal,
                            'ps_notequal': ps_notequal, 'ps_notfound': ps_notfound, 'ps_equal_total': ps_equal_total,
                            'ps_notequal_total': ps_notequal_total, 'direction':direction, 'username': auth.get_user(request).username}
                    return render(request, self.template_name, args)

            if submitbutton == 'update':
                simplelist = self.simplelist
                for i in range(0, len(simplelist)):
                    files = simplelist[i].getFiles()
                    name = simplelist[i].getName()
                    for j in files:
                        if name == 'kaspi':
                            kaspi = KaspiParser(j,request)
                            kaspi.getParse()
                        if names[i] == 'processing':
                            nurbank = NurbankParser(j,request)
                            nurbank.getParse()
                        if names[i] == 'tourism':
                            tourism = ToursimParser(j,request)
                            tourism.getParse()
                        if names[i] == 'kazkom':
                            kazkom = KazkomParser(j,request)
                            kazkom.getParse()
                direction = "ChocoToPayment"
                return render(request, self.template_name, {'direction':direction})



class ParseForm(TemplateView):
    template_name = 'project/update_list.html'

    # simplelist = []
    # for i in range(0, len(names)):
    #         files = []
    #         th = Parser(names[i], files)
    #         th.start()
    #         file = th.file
    #         x = Payment(names[i], file)
    #         simplelist.append(x)

    def get(self, request):
        return render(request, self.template_name, {})
    def post(self,request):
        # #getFilenames---------------
        # submitbutton = request.POST.get('submit')
        # if(submitbutton == 'Search'):
        #     newFiles = False
        #     simplelist = self.simplelist
        #     if len(simplelist) > 0 :
        #         newFiles = True
        #     args = {'bank': simplelist[0].getName(), 'files': simplelist[0].getFiles(), 'newFiles': newFiles, 'button':submitbutton}
        #     return render(request, 'project/update_list.html', args)
        #
        # if submitbutton == "Parse":
        #     simplelist = self.simplelist
        #     for i in range(0, len(simplelist)):
        #         files = simplelist[i].getFiles()
        #         name = simplelist[i].getName()
        #         for j in files:
        #             if name == 'kaspi':
        #                 kaspi = KaspiParser(j)
        #                 kaspi.getParse()
        #             if names[i] == 'processing':
        #                 nurbank = NurbankParser(j)
        #                 nurbank.getParse()
        #             if names[i] == 'tourism':
        #                 tourism = ToursimParser(j)
        #                 tourism.getParse()
        #             if names[i] == 'kazkom':
        #                 kazkom = KazkomParser(j)
        #                 kazkom.getParse()
        return redirect('/transaction')


def update_list(request):
     return render(request, 'project/update_list.html', {})

def index(request):
    return render(request,'project/index.html', {})

class UpdatedData:
    def __init__(self, id, date, time, reference, transfer, fee, total, bank, update_time):
        self.id = id
        self.date = date
        self.time=time
        self.reference = reference
        self.transfer = transfer
        self.fee = fee
        self.total = total
        self.bank = bank
        self.update_time = update_time

        def getArr(self):
            data = {
                'id': self.id,
                'date':self.date,
                'time': self.time,
                'transfer': self.transfer,
                'reference': self.reference,
                'fee':self.fee,
                'total': self.total,
                'updated_time': self.update_time,
                'bank':self.bank
            }
            return data


class History(TemplateView):
    template_name = 'project/History.html'


    def get(self, request):
        # found = False
        return render(request, self.template_name, {})

    def post(self, request):
        button = request.POST.get("find")
        id = request.POST.get('id')
        reference = request.POST.get('reference')
        found = False
        name = request.POST.get("name")

        if button == "range":
            start = request.POST.get("start_date")
            end = request.POST.get("end_date")

            transactions = UpdatedTransaction.objects.filter(name=name,date__range=[start, end])
            if transactions:
                found = True
            list = []
            for i in transactions:
                list.append(UpdatedData(i.ids, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name, i.update_time))
            # for i in list:
            #     print(i.id)

            create_action(request.user, 'Searched updated transactions between %s and %s in %s' % (start, end, name),0)
            return render(request, self.template_name, {'found': found, 'list': list, 'username': auth.get_user(request).username})

        if button == "id":
            transactions = UpdatedTransaction.objects.filter(ids = id, name=name)
            if transactions:
                found = True
            list = []
            for i in transactions:
                list.append(UpdatedData(i.ids, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name, i.update_time))
            create_action(request.user,
                          'Searched updated transaction by id: %s' % (id), list[0].id)

            return render(request, self.template_name, {'found': found, 'list': list, 'username': auth.get_user(request).username})

        if button == "reference":
            transactions = UpdatedTransaction.objects.filter(reference = reference, name=name)
            if transactions:
                found = True
            list = []

            transactions = transactions.order_by('date', 'update_time', 'time')
            for i in transactions:
                list.append(UpdatedData(i.ids, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name, i.update_time))

            create_action(request.user,
                          'Searched updated transaction by reference: %s' %(reference), list[0].id)
            return render(request, self.template_name, {'found': found, 'list': list, 'username': auth.get_user(request).username})



        args = {'found': found}
        return render(request, self.template_name, args)

class Analytics(TemplateView):
    template_name = 'project/Analytics.html'

    def get(self, request):
        return render(request, self.template_name, {})