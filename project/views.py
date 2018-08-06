import datetime
import json
from dateutil import parser
from collections import namedtuple

# from django.core.mail.backends import console
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from project.forms import PostForm
from .models import Transaction
from project.forms import UpdateForm
from project.GmailParser import Parser
from project.models import Payment,KaspiParser,NurbankParser,KazkomParser,ToursimParser
import logging
logger = logging.getLogger(__name__)
from project.models import Data
# import win32api?/

# Create your views here.

#user registration
# time
# add time and compare
# buttons
#logs

ids = [1,2,3,4]
names = ['kaspi', 'processing', 'tourism', 'kazkom']

class FormView(TemplateView):
    template_name = 'project/transaction_list.html'

    simplelist = []
    # console.show_activity('Checking for update...')
    for i in range(0, len(names)):
        files = []
        th = Parser(names[i], files)
        th.start()
        file = th.file
        x = Payment(names[i], file)
        simplelist.append(x)

    def get(self, request):
        form = PostForm()
        return render(request, self.template_name, {'form':form})

    def post(self,request):
        # form = PostForm(request.POST)
        # if form.is_valid():
            # name = form.cleaned_data['name']
        submitbutton = request.POST.get("submit")
        if (submitbutton == 'search'):
            name = request.POST.get("name")
            start = request.POST.get("start_date")
            end = request.POST.get("end_date")
                # start = form.cleaned_data['start_date']
                # end = form.cleaned_data['end_date']
                # start = datetime.date(2018,7,20)
                # end = datetime.date(2018,8,20)
                # by dates
            filename = '/home/mrx/Documents/choko-master/docs/api.json'
            myfile = open(filename, 'r', encoding='Latin-1')
            json_data = json.load(myfile)
    #------------------------------------------------------------------------------------------------------------------------

            equal = []
            notequal = []
            notfound = []

            equal_total = Data(' ', ' ', 0, 0, 0, ' ')
            notequal_total = Data(' ', ' ', 0, 0, 0, ' ')

            for data in json_data:
                if data['payment_code'] == name.upper():
                    tr = Transaction.objects.filter(id = data['order_id'],date__range=[start, end])
                    if len(tr) > 0:
                        for i in tr:
                            if i.transfer == data['payment_amount']:
                                a = Data(i.id, i.date, i.transfer, i.fee, i.total, i.name)
                                b = Data(data['order_id'], datetime.datetime.date(parser.parse(data['date_created'])),
                                             data['payment_amount'], 0, data['payment_amount'], 'Chocotravel/Aviata')
                                equal.append(a)
                                equal.append(b)
                                equal_total.transfer = float(equal_total.transfer) + float(a.transfer)
                                equal_total.fee = float(equal_total.fee) + float(a.fee)
                                equal_total.total = float(equal_total.total) + float(a.total)
                            else:
                                a = Data(i.id, i.date, i.transfer, i.fee, i.total, i.name)
                                b = Data(data['order_id'], datetime.datetime.date(parser.parse(data['date_created'])),
                                             data['payment_amount'], 0, data['payment_amount'], 'Chocotravel/Aviata')
                                notequal.append(a)
                                notequal.append(b)
                                notequal_total.transfer = notequal_total.transfer + a.transfer
                                notequal_total.fee = notequal_total.fee + a.fee
                                notequal_total.total = notequal_total.total + a.total
                    else:
                        notfound.append(Data(data['order_id'], datetime.datetime.date(parser.parse(data['date_created'])),
                                             data['payment_amount'], 0, data['payment_amount'], 'Chocotravel/Aviata'))

                #-----------------------------------------------------------------------------------------------------------

            ps_equal = []
            ps_notequal = []
            ps_notfound = []
            ps_equal_total = Data(' ', ' ', 0, 0, 0, ' ')
            ps_notequal_total =  Data(' ', ' ', 0, 0, 0, ' ')

            transactions = Transaction.objects.filter(name__contains=name, date__range=[start, end])
            print(len(transactions))
            print(len(json_data))
            for i in transactions:
                # for data in json_data:
                output_dict = [x for x in json_data if x['order_id'] == i.id and x['payment_code'] == name.upper()]
                data = json.dumps(output_dict)
                # print(data[0]['payment_amount'])
                # if(len(data) > 0):
                #         # print("id compared")
                #     if i.transfer == data['payment_amount']:
                #         print("payment compared")
                #         a = Data(i.id, i.date, i.transfer, i.fee, i.total, i.name)
                #         b = Data(data['order_id'], datetime.datetime.date(parser.parse(data['date_created'])),
                #                      data['payment_amount'], 0, data['payment_amount'], 'Chocotravel/Aviata')
                #         ps_equal.append(a)
                #         ps_equal.append(b)
                #         ps_equal_total.transfer = ps_equal_total.transfer + a.transfer
                #         ps_equal_total.fee = ps_equal_total.fee + a.fee
                #         ps_equal_total.total = ps_equal_total.total + a.total
                #     else:
                #         a = Data(i.id, i.date, i.transfer, i.fee, i.total, i.name)
                #         b = Data(data['order_id'], datetime.datetime.date(parser.parse(data['date_created'])),
                #                          data['payment_amount'], 0, data['payment_amount'], 'Chocotravel/Aviata')
                #         ps_notequal.append(a)
                #         ps_notequal.append(b)
                #         ps_notequal_total.transfer = ps_notequal_total.transfer + a.transfer
                #         ps_notequal_total.fee = ps_notequal_total.fee + a.fee
                #         ps_notequal_total.total = ps_notequal_total.total + a.total
                # else:
                #         ps_notfound.append(Data(i.id, i.date, i.transfer, i.fee, i.total, i.name))
                # #'form':form
            print(len(equal))
            print(len(ps_equal))
            print()
            args = {'name': name, 'equal': equal, 'notequal':notequal, 'notfound': notfound, 'equal_total':equal_total, 'notequal_total': notequal_total, 'ps_equal': ps_equal,'ps_notequal': ps_notequal, 'ps_notfound': ps_notfound, 'ps_equal_total':ps_equal_total, 'ps_notequal_total':ps_notequal_total}
            return render(request, self.template_name, args)
        if submitbutton == 'update':
            simplelist = self.simplelist
            for i in range(0, len(simplelist)):
                files = simplelist[i].getFiles()
                name = simplelist[i].getName()
                for j in files:
                    if name == 'kaspi':
                        kaspi = KaspiParser(j)
                        kaspi.getParse()
                    if names[i] == 'processing':
                        nurbank = NurbankParser(j)
                        nurbank.getParse()
                    if names[i] == 'tourism':
                        tourism = ToursimParser(j)
                        tourism.getParse()
                    if names[i] == 'kazkom':
                        kazkom = KazkomParser(j)
                        kazkom.getParse()
            found = True

            return render(request, self.template_name, { 'found':found })


class ParseForm(TemplateView):
    template_name = 'project/update_list.html'

    simplelist = []
    for i in range(0, len(names)):
            files = []
            th = Parser(names[i], files)
            th.start()
            file = th.file
            x = Payment(names[i], file)
            simplelist.append(x)

    def get(self, request):
        return render(request, self.template_name, {})
    def post(self,request):
        #getFilenames---------------
        submitbutton = request.POST.get('submit')
        if(submitbutton == 'Search'):
            newFiles = False
            simplelist = self.simplelist
            if len(simplelist) > 0 :
                newFiles = True
            args = {'bank': simplelist[0].getName(), 'files': simplelist[0].getFiles(), 'newFiles': newFiles, 'button':submitbutton}
            return render(request, 'project/update_list.html', args)

        if submitbutton == "Parse":
            simplelist = self.simplelist
            for i in range(0, len(simplelist)):
                files = simplelist[i].getFiles()
                name = simplelist[i].getName()
                for j in files:
                    if name == 'kaspi':
                        kaspi = KaspiParser(j)
                        kaspi.getParse()
                    if names[i] == 'processing':
                        nurbank = NurbankParser(j)
                        nurbank.getParse()
                    if names[i] == 'tourism':
                        tourism = ToursimParser(j)
                        tourism.getParse()
                    if names[i] == 'kazkom':
                        kazkom = KazkomParser(j)
                        kazkom.getParse()
        return redirect('/transaction')

def update_list(request):
     return render(request, 'project/update_list.html', {})

def index(request):
    return render(request,'project/index.html', {})
