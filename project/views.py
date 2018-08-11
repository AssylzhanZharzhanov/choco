import csv
import datetime
import json
import xlwt
from dateutil import parser
from collections import namedtuple
from django.contrib.auth.models import User
from django.contrib import auth
from django.http import HttpResponse
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
import plotly.offline as opy
import plotly.graph_objs as go
# from project.models import Payment,KaspiParser,NurbankParser,KazkomParser,ToursimParser
import logging
from project.models import UpdatedTransaction
from actions.utils import create_action
from .models import Task
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
            # updated = UpdatedTransaction(ids=datas[i]['id'], date=datas[i]['date'], time=datas[i]['time'],
            #                              name=datas[i]['bank'], transfer=datas[i]['transfer'],
            #                              fee=datas[i]['fee'], total=datas[i]['total'], update_time=datas[i]['time'],
            #                              company="Chocotravel/Aviata",
            #                              reference=datas[i]['reference'])
            # updated.save()
        else:
             if datas[i]['time'] > transactions.get(date=datas[i]['date']).time and datas[i]['date'] >= transactions.get(date=datas[i]['date']).date :
                 Transaction.objects.filter(id = datas[i]['id'],date = datas[i]['date']).update(time = datas[i]['time'], transfer=datas[i]['transfer'], fee=datas[i]['fee'], total=datas[i]['total'], updated=True, update_time=datas[i]['time'], company="Chocotravel/Aviata",reference=datas[i]['reference'])
                 updated = UpdatedTransaction(ids = datas[i]['id'],date = datas[i]['date'],time = datas[i]['time'], name = datas[i]['bank'], transfer=datas[i]['transfer'],
                                  fee=datas[i]['fee'], total=datas[i]['total'], update_time=datas[i]['time'], company="Chocotravel/Aviata",
                                  reference=datas[i]['reference'], fixed=False, updated_date = datas[i]['date'])
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
notequals_to_fix = []
ids = [1,2,3,4]
names = ['kaspi', 'processing', 'tourism', 'kazkom']
def getUsers():
    financiers = User.objects.all()
    financiers_username = []
    for i in financiers:
        financiers_username.append(i.username)
    financiers_username.remove('admin')
    return financiers_username


class FormView(TemplateView):
    global seq, snon, sfound, columns
    template_name = "project/transaction_list.html"
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
        financiers = getUsers()

        return render(request, self.template_name, {'form':form, 'direction':direction, 'username': auth.get_user(request).username})

    def getJson(self, str):
        print(str)
        if str[5] == 'midnight':
            data = {
                'id': str[1],
                'date': str[2] + " " + str[3] + " " + str[4],
                'time': "00:00",
                'transfer': str[6],
                'fee': str[7],
                'total':str[8],
                'reference':str[9],
                'bank': str[10],
                'status':str[11]
            }
        else:
            data = {
                'id': str[1],
                'date': str[2] + " " + str[3] + " " + str[4],
                'time': str[5] + " " + str[6],
                'transfer': str[7],
                'fee': str[8],
                'total': str[9],
                'reference': str[10],
                'bank': str[11],
                'status': str[12]
            }

        return data

    def post(self,request):
        global seq_total, snon_total
        columns = ['id', 'date', 'time', 'transfer', 'fee', 'total', 'reference', 'bank']
        submitbutton = request.POST.get("submit")
        fixbutton = request.POST.get("fix")
        name = request.POST.get("name")
        request.session["bank"] = name
        start = request.POST.get("start_date")
        end = request.POST.get("end_date")
        request.session['start'] = start
        request.session['end'] = end
        direction = request.POST.get("direction")
        company =request.POST.get("company")
        filename = '/home/mrx/Documents/choko-master/docs/api.json'
        myfile = open(filename, 'r', encoding='Latin-1')
        json_data = json.load(myfile)
        send_message = request.POST.get("send")
  #------------------------------------fix-------------------------------
        if not request.user.is_authenticated:
            args = {'message': "Please enter your username and password! "}
            return render(request, 'login.html', args)
        else:
            if send_message == 'send':
                start = request.POST.get("start")
                end = request.POST.get("end")
                request.session['start'] = start
                request.session['end'] = end
                selected_user = request.POST.get("workers")
                selected_ids = json.loads(request.POST.get("selected_ids"))
                datas = []
                for i in selected_ids:
                    data = self.getJson(i.split(' '))
                    datas.append(data)
                for i in datas:
                    print(i)
                for i in datas:
                    message = Task(user=selected_user,ids=i['id'], time=datetime.datetime.time(parser.parse(i['time'])), date=datetime.datetime.date(parser.parse(i['date'])),
                                   name=i['bank'], transfer= float(i['transfer']), fee=float(i['fee']), total=float(i['total']), reference=i['reference'], status=i['status'], comment=' ')
                    message.save()
                    create_action(request.user, "Admin gave a task to %s inform transaction by id: %s" %(selected_user, i['id']), i['id'])

                    # print(datetime.datetime.date(parser.parse(i['date'])))
                    # print(datetime.datetime.time(parser.parse(i['time'])))

                direction = "ChocoToPayment"
                # args = {'equal': seq, 'notequal': snon, 'notfound': sfound,
                #             'equal_total': seq_total, 'notequal_total': snon_total}
                return render(request, self.template_name,{'name': name, 'direction':direction, 'username': auth.get_user(request).username})

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
                                Transaction.objects.filter(id=Fix[i].id).update(fixed=True)
                                updateTransaction = UpdatedTransaction(ids = transactions.id, date = transactions.date, update_date = datetime.datetime.date(datetime.datetime.now()), time = transactions.time, name = transactions.name, transfer=transactions.transfer,
                                      fee=transactions.fee, total=transactions.total, update_time=datetime.datetime.time(datetime.datetime.now()), company=transactions.company,
                                      reference=transactions.reference, fixed=True)
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
                            tr = Transaction.objects.filter(id = data['order_id'],date__range=[start, end],company=company)
                            if len(tr) > 0:
                                for i in tr:
                                    if i.transfer == data['payment_amount'] and i.reference == data['payment_reference']:
                                        a = Data(i.id, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name)
                                        b = Data(data['order_id'], datetime.datetime.date(parser.parse(data['date_created'])),
                                                 datetime.datetime.time(parser.parse(data['date_created'])),
                                                 data['payment_reference'], data['payment_amount'], 0, data['payment_amount'],
                                                 company)
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
                                                 company)
                                        notequal.append(a)
                                        notequal.append(b)
                                        notequal_total.transfer = notequal_total.transfer + a.transfer
                                        notequal_total.fee = notequal_total.fee + a.fee
                                        notequal_total.total = notequal_total.total + a.total
                            else:
                                notfound.append(Data(data['order_id'], datetime.datetime.date(parser.parse(data['date_created'])),
                                                     datetime.datetime.time(parser.parse(data['date_created'])), data['payment_reference'],
                                                     data['payment_amount'], 0, data['payment_amount'], company))
                    global  fix_datas
                    fix_datas = notequal
                    datas = notequal
                    seq = equal
                    snon = notequal
                    sfound = notfound
                    seq_total = equal_total
                    snon_total = notequal_total

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
                    transactions = Transaction.objects.filter(name__contains=name, date__range=[start, end], company=company)
                    # print(len(transactions))
                    for i in transactions:
                        data = [x for x in json_data if x['order_id'] == i.id and x['payment_code'] == name.upper()]
                        if len(data) > 0:
                            if(data[0]['payment_amount'] == i.transfer and  i.reference == data[0]['payment_reference']):
                                a = Data(i.id, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name)
                                b = Data(data[0]['order_id'], datetime.datetime.date(parser.parse(data[0]['date_created'])),
                                         datetime.datetime.time(parser.parse(data[0]['date_created'])),data[0]['payment_reference'],
                                         data[0]['payment_amount'], 0, data[0]['payment_amount'], company)
                                ps_equal.append(a)
                                ps_equal.append(b)
                                ps_equal_total.transfer = ps_equal_total.transfer + a.transfer
                                ps_equal_total.fee = ps_equal_total.fee + a.fee
                                ps_equal_total.total = ps_equal_total.total + a.total
                            elif data[0]['payment_amount'] != i.transfer  and i.reference == data[0]['payment_reference']:
                                a = Data(i.id, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name)
                                b = Data(data[0]['order_id'], datetime.datetime.date(parser.parse(data[0]['date_created'])),
                                         datetime.datetime.time(parser.parse(data[0]['date_created'])),
                                         data[0]['payment_reference'],
                                         data[0]['payment_amount'], 0, data[0]['payment_amount'], company)
                                ps_notequal.append(a)
                                ps_notequal.append(b)
                                ps_notequal_total.transfer = ps_notequal_total.transfer + a.transfer
                                ps_notequal_total.fee = ps_notequal_total.fee + a.fee
                                ps_notequal_total.total = ps_notequal_total.total + a.total
                        else:
                            ps_notfound.append(Data(i.id, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name))

                    create_action(request.user, 'Searched transactions of %s between %s and %s' % (company,start, end),0  )
                    seq = ps_equal
                    snon = ps_notequal
                    sfound = ps_notfound
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

            if(submitbutton == "download"):
                global seq
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment;filename=export_equal.csv'
                writer = csv.writer(response)
                writer.writerow(columns)
                for obj in seq:
                    writer.writerow([getattr(obj, field) for field in columns])
                return response

            if (submitbutton == "nondownload"):
                global snon
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment;filename=export_not_equal.csv'
                writer = csv.writer(response)
                writer.writerow(columns)
                for obj in snon:
                    writer.writerow([getattr(obj, field) for field in columns])
                return response

            if (submitbutton == "founddownload"):
                global sfound
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment;filename=export_not_found.csv'
                writer = csv.writer(response)
                writer.writerow(columns)
                for obj in sfound:
                    writer.writerow([getattr(obj, field) for field in columns])
                return response

            if (submitbutton == "excel"):
                global seq
                print("excel")
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename=equal.xls'
                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet("Equal")

                row_num = 0

                font_style = xlwt.XFStyle()
                font_style.font.bold = True

                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)

                font_style = xlwt.XFStyle()
                font_style.alignment.wrap = 1

                for obj in seq:
                    row_num += 1
                    row = [
                        obj.id,
                        obj.date,
                        obj.transfer,
                        obj.fee,
                        obj.total,
                        obj.bank,
                    ]
                    for col_num in range(len(row)):
                        ws.write(row_num, col_num, row[col_num], font_style)

                wb.save(response)
                return response

            if (submitbutton == "foundexcel"):
                global sfound
                print("foundexcel")
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename=not_found.xls'
                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet("NotFound")

                row_num = 0

                font_style = xlwt.XFStyle()
                font_style.font.bold = True

                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)

                font_style = xlwt.XFStyle()
                font_style.alignment.wrap = 1

                for obj in sfound:
                    row_num += 1
                    row = [
                        obj.id,
                        obj.date,
                        obj.transfer,
                        obj.fee,
                        obj.total,
                        obj.bank,
                    ]
                    for col_num in range(len(row)):
                        ws.write(row_num, col_num, row[col_num], font_style)

                wb.save(response)
                return response

            if (submitbutton == "nonexcel"):
                global snon
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename=notequal.xls'
                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet("Equal")

                row_num = 0

                font_style = xlwt.XFStyle()
                font_style.font.bold = True

                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)

                font_style = xlwt.XFStyle()
                font_style.alignment.wrap = 1
                for obj in snon:
                    row_num += 1
                    row = [
                        obj.id,
                        obj.date,
                        obj.transfer,
                        obj.fee,
                        obj.total,
                        obj.bank,
                    ]
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style)

                wb.save(response)
                return response

            if (submitbutton == "download"):
                global seq
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment;filename=export_equal.csv'
                writer = csv.writer(response)
                writer.writerow(columns)
                for obj in seq:
                    writer.writerow([getattr(obj, field) for field in columns])
                return response

            if (submitbutton == "nondownload"):
                global snon
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment;filename=export_not_equal.csv'
                writer = csv.writer(response)
                writer.writerow(columns)
                for obj in snon:
                    writer.writerow([getattr(obj, field) for field in columns])
                return response

            if (submitbutton == "founddownload"):
                global sfound
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment;filename=export_not_found.csv'
                writer = csv.writer(response)
                writer.writerow(columns)
                for obj in sfound:
                    writer.writerow([getattr(obj, field) for field in columns])
                return response

            if (submitbutton == "excel"):
                global seq
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename=equal.xls'
                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet("Equal")

                row_num = 0

                font_style = xlwt.XFStyle()
                font_style.font.bold = True

                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)

                font_style = xlwt.XFStyle()
                font_style.alignment.wrap = 1

                for obj in seq:
                    row_num += 1
                    row = [
                        obj.id,
                        obj.date,
                        obj.transfer,
                        obj.fee,
                        obj.total,
                        obj.bank,
                    ]
                    for col_num in range(len(row)):
                        ws.write(row_num, col_num, row[col_num], font_style)

                wb.save(response)
                return response

            if (submitbutton == "foundexcel"):
                global sfound
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename=not_found.xls'
                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet("NotFound")

                row_num = 0

                font_style = xlwt.XFStyle()
                font_style.font.bold = True

                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)

                font_style = xlwt.XFStyle()
                font_style.alignment.wrap = 1

                for obj in sfound:
                    row_num += 1
                    row = [
                        obj.id,
                        obj.date,
                        obj.transfer,
                        obj.fee,
                        obj.total,
                        obj.bank,
                    ]
                    for col_num in range(len(row)):
                        ws.write(row_num, col_num, row[col_num], font_style)

                wb.save(response)
                return response

            if (submitbutton == "nonexcel"):
                global snon
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename=notequal.xls'
                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet("Equal")

                row_num = 0

                font_style = xlwt.XFStyle()
                font_style.font.bold = True

                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)

                font_style = xlwt.XFStyle()
                font_style.alignment.wrap = 1
                for obj in snon:
                    row_num += 1
                    row = [
                        obj.id,
                        obj.date,
                        obj.transfer,
                        obj.fee,
                        obj.total,
                        obj.bank,
                    ]
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style)

                wb.save(response)
                return response


class UpdatedData:
    def __init__(self, id, date, time, reference, transfer, fee, total, bank, update_time, updated_date, fixed):
        self.id = id
        self.date = date
        self.time=time
        self.reference = reference
        self.transfer = transfer
        self.fee = fee
        self.total = total
        self.bank = bank
        self.update_time = update_time
        self.updated_date = updated_date
        self.fixed = fixed

        def getArr(self):
            data = {
                'id': self.id,
                'date':self.date,
                'updated_date':self.updated_date,
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
        found = True
        return render(request, self.template_name, {'found':found})

    def post(self, request):
        if not request.user.is_authenticated:
            args = {'message': "Please enter your username and password! "}
            return render(request, 'login.html', args)
        else:
            button = request.POST.get("find")
            id = request.POST.get('id')
            reference = request.POST.get('reference')

            name = request.POST.get("name")

            if button == "range":
                start = request.POST.get("start_date")
                end = request.POST.get("end_date")
                found = False
                transactions = UpdatedTransaction.objects.filter(name=name, date__range=[start, end])
                print(transactions)
                if transactions:
                    found = True

                list = []

                for i in transactions:
                    if i.fixed == True:
                        list.append(UpdatedData(i.ids, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name, i.update_time, i.update_date, 'fixed'))
                    else:
                        list.append(UpdatedData(i.ids, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name,
                                                i.update_time, i.update_date, 'not fixed'))

                create_action(request.user, 'Searched updated transactions between %s and %s in %s' %(start, end, name),0)
                return render(request, self.template_name, {'found': found, 'list': list, 'username': auth.get_user(request).username})

            if button == "id":
                found = False
                transactions = UpdatedTransaction.objects.filter(ids = id)
                if transactions:
                    found = True
                list = []
                for i in transactions:
                    list.append(UpdatedData(i.ids, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name, i.update_time, i.update_date))
                if found:
                    create_action(request.user,
                              'Searched updated transaction by id: %s' % (id), id)
                else:
                    create_action(request.user,
                                  'Failed in searching updated transaction by id: %s' % (id), id)

                return render(request, self.template_name, {'found': found, 'list': list, 'username': auth.get_user(request).username})

            if button == "reference":
                found = False
                transactions = UpdatedTransaction.objects.filter(reference = reference)

                if transactions:
                    found = True
                list = []

                # transactions = transactions.order_by('date', 'update_time', 'time')
                for i in transactions:
                    list.append(UpdatedData(i.ids, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name, i.update_time, i.update_date))
                # id = UpdatedTransaction.objects.get(reference=reference).ids
                # print(id)

                if found:
                    create_action(request.user,
                              'Searched updated transaction by reference: %s' %(reference), list[0].id)
                else:
                    create_action(request.user,
                                  ' Failed in searching updated transaction by reference: %s' % (reference), -1)

                return render(request, self.template_name, {'found': found, 'list': list, 'username': auth.get_user(request).username})


            # args = {'found': found}
            # return render(request, self.template_name, args)

# -------------------------------------------------------Analysis-----------------------------------
class Analytics(TemplateView):
    template_name = 'project/Analytics.html'
    # global seq, snon, sfound, columns

    def get(self, request):
        if seq:
            data = []
            y = []
            for i in seq:
                y.append(i.getArr())

            if len(y)>0:
                df = pd.DataFrame(y)

                trace1 = go.Scatter(
                    x=df.date,
                    y=df.date.value_counts().tolist(),
                    name="Datas with equal parameters",
                    line=dict(color='#17BECF'),
                    opacity=0.8)
                data.append(trace1)

            x = []
            for i in snon:
                x.append(i.getArr())

            if len(x)>0:
                df2 = pd.DataFrame(x)
                trace2 = go.Scatter(
                    x=df2.date,
                    y=df2.id.value_counts().tolist(),
                    name="Datas with not equal trasnfer amount",
                    opacity=0.8)
                data.append(trace2)

            z = []
            for i in sfound:
                z.append(i.getArr())

            if len(z)>0:
                df3 = pd.DataFrame(z)
                trace3 = go.Scatter(
                    x=df3.date,
                    y=df3.date.value_counts().tolist(),
                    name = "Datas not found in database",
                    line=dict(color='#7F7F7F'),
                    opacity=0.8
                )
                data.append(trace3)

            layout = dict(
                title='Time Series',
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1,
                                 label='everyday',
                                 step='day',
                                 stepmode='todate'),
                            dict(count=7,
                                 label='everyweek',
                                 step='day',
                                 stepmode='backward'),
                            dict(count=6,
                                 label='everymonth',
                                 step='month',
                                 stepmode='backward'),
                            dict(step='all')
                        ])
                    ),
                    rangeslider=dict(
                        visible=True
                    ),
                    type='date'
                )
            )
            figure = go.Figure(data=data, layout=layout)
            div = opy.plot(figure, auto_open=False, output_type='div')
            args = {'graph': div}

            return render(request, self.template_name, args)
        else:
            return render(request, self.template_name, {})

    def post(self, request):

        if not request.user.is_authenticated:
            args = {'message': "Please enter your username and password! "}
            return render(request, 'login.html', args)

        return render(request, self.template_name, {})



def getNotEqual(start, end):
    filename = '/home/mrx/Documents/choko-master/docs/api.json'
    myfile = open(filename, 'r', encoding='Latin-1')
    json_data = json.load(myfile)

    datas = []
    equal = []
    notequal = []
    notfound = []

    for data in json_data:
            tr = Transaction.objects.filter(id=data['order_id'], date__range=[start, end])
            if len(tr) > 0:
                for i in tr:
                    if i.transfer == data['payment_amount'] and i.reference == data['payment_reference']:
                        a = Data(i.id, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name)
                        b = Data(data['order_id'], datetime.datetime.date(parser.parse(data['date_created'])),
                                 datetime.datetime.time(parser.parse(data['date_created'])),
                                 data['payment_reference'], data['payment_amount'], 0, data['payment_amount'],
                                 Transaction.objects.get(id=data['order_id'], date__range=[start, end]).company)
                        equal.append(a)
                        equal.append(b)
                    elif i.transfer != data['payment_amount'] and i.reference == data['payment_reference']:
                        a = Data(i.id, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name)
                        b = Data(data['order_id'],
                                 datetime.datetime.date(parser.parse(data['date_created'])),
                                 datetime.datetime.time(parser.parse(data['date_created'])),
                                 data['payment_reference'],
                                 data['payment_amount'], 0, data['payment_amount'],
                                 Transaction.objects.get(id=data['order_id'], date__range=[start, end]).company)
                        notequal.append(a)
                        notequal.append(b)
            return notequal


class TaskData:
    def __init__(self, id, date, time, reference, transfer, fee, total, bank, user, comment):
        self.id = id
        self.date = date
        self.time = time
        self.reference = reference
        self.transfer = transfer
        self.fee = fee
        self.total = total
        self.bank = bank
        self.user = user
        self.comment = comment

    def getArr(self):
        data = {
            'id': self.id,
            'date': self.date,
            'time': self.time,
            'transfer': self.transfer,
            'reference': self.reference,
            'fee': self.fee,
            'total': self.total,
            'bank': self.bank,
            'user':self.user,
            'comment': self.comment
        }
        return data


class Tasks(TemplateView):
    template_name = 'project/Tasks.html'

    def get(self, request):
        if not request.user.is_authenticated:
            args = {'message': "Please enter your username and password! "}
            return render(request, 'login.html', args)

        if str(request.user) == 'admin':
            notequal = Task.objects.filter(status="notequal")
            notfound = Task.objects.filter(status="notfound")
            equal = Task.objects.filter(status="equal")

            notequal_list= []
            notfound_list= []
            equal_list = []

            for i in notequal:
                data = TaskData(i.ids,i.date,i.time,i.reference,i.transfer,i.fee,i.total,i.name,i.user,i.comment)
                notequal_list.append(data)

            for i in notequal_list:
                print(i.user, i.id, i.comment)

            for i in notfound:
                data = TaskData(i.ids, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name,i.user,i.comment)
                notfound_list.append(data)

            for i in equal:
                data = TaskData(i.ids, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name,i.user,i.comment)
                equal_list.append(data)

            return render(request, self.template_name, {'notequal':notequal_list, 'notfound':notfound_list, 'equal': equal_list})

        if str(request.user) != 'admin':
            username = request.user
            notequal = Task.objects.filter(user=username, status="notequal")
            notfound = Task.objects.filter(user=username, status="notfound")
            equal = Task.objects.filter(user=username, status="equal")

            notequal_list= []
            notfound_list= []
            equal_list = []

            for i in notequal:
                data = TaskData(i.ids,i.date,i.time,i.reference,i.transfer,i.fee,i.total,i.name,i.user,i.comment)
                notequal_list.append(data)

            for i in notfound:
                data = TaskData(i.ids, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name,i.user,i.comment)
                notfound_list.append(data)

            for i in equal:
                data = TaskData(i.ids, i.date, i.time, i.reference, i.transfer, i.fee, i.total, i.name,i.user,i.comment)
                equal_list.append(data)

            return render(request, self.template_name, {'notequal':notequal_list, 'notfound':notfound_list, 'equal': equal_list})

        return render(request, self.template_name, {})

    def post(self, request):
        username = request.user
        fix_button = request.POST.get("fix")
        send = request.POST.get("send")

        #POST send comment
        if send == 'send':
            user = request.POST.get("user")
            comment = request.POST.get("comment")
            selected_ids = json.loads(request.POST.get("selected_ids"))
            print(selected_ids)
            ids_arr = []
            for i in selected_ids:
                str = i.split(' ')
                for j in str:
                    if j == '':
                        continue
                    ids_arr.append(j)

            for i in ids_arr:
                Task.objects.filter(user=user, ids = i).update(comment=comment)
                create_action(request.user,
                              'Inserted comment transaction to transaction which id: %s' % (i), i)

            return self.get(request)

        #fix datas
        if fix_button == 'fix':
            ids = json.loads(request.POST.get("ids"))
            ids_arr = []
            for i in ids:
                str = i.split(' ')
                for j in str:
                    if j == ' ':
                        continue
                    ids_arr.append(j)

            filename = '/home/mrx/Documents/choko-master/docs/api.json'
            myfile = open(filename, 'r', encoding='Latin-1')
            json_data = json.load(myfile)

            # fix_datas = Task.objects.filter(user=username, )

            # for i in range(0, len(fix_datas)):
            #     if (i % 2 == 0):
            #         notFix.append(fix_datas[i])
            #     else:
            #         Fix.append(fix_datas[i])
            #
            # for i in range(0, len(Fix)):
            #     if (Fix[i].transfer != notFix[i].transfer):
            #         for x in json_data:
            #             if x['order_id'] == Fix[i].id and x['payment_reference'] == Fix[i].reference:
            #                 x['payment_amount'] = notFix[i].transfer
            #                 transactions = Transaction.objects.get(id=Fix[i].id, reference=Fix[i].reference)
            #                 Transaction.objects.filter(id=Fix[i].id).update(fixed=True)
            #                 updateTransaction = UpdatedTransaction(ids=transactions.id, date=transactions.date,
            #                                                        update_date=datetime.datetime.date(
            #                                                            datetime.datetime.now()), time=transactions.time,
            #                                                        name=transactions.name,
            #                                                        transfer=transactions.transfer,
            #                                                        fee=transactions.fee, total=transactions.total,
            #                                                        update_time=datetime.datetime.time(
            #                                                            datetime.datetime.now()),
            #                                                        company=transactions.company,
            #                                                        reference=transactions.reference, fixed=True)
            #                 updateTransaction.save()
            #                 print(request.session["bank"])
            #                 create_action(request.user,
            #                               "Fixed %s datas by id: %s" % (transactions.name, transactions.id),
            #                               transactions.id)


            for i in ids_arr:
                print(i)

        # Task.objects.filter(user=username, id =)

        return self.get(request)

