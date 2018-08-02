import datetime
import json
from dateutil import parser
from collections import namedtuple
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
# Create your views here.

class FormView(TemplateView):
    template_name = 'project/transaction_list.html'

    def get(self, request):
        form = PostForm()
        return render(request, self.template_name, {'form':form})

    def post(self,request):
        form = PostForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            # start = form.cleaned_data['start_date']
            # end = form.cleaned_data['end_date']
            start = datetime.date(2018,7,20)
            end = datetime.date(2018,8,20)
            transactions = Transaction.objects.filter(name__contains=name, date__range=[start, end])
                # by dates
            filename = '/home/mrx/Documents/choko-master/docs/api.json'
            myfile = open(filename, 'r', encoding='Latin-1')
            json_data = json.load(myfile)

            equal = []
            notequal = []

            for data in json_data:
                if data['payment_code'] == name.upper():
                    tr = Transaction.objects.filter(id = data['order_id'])
                    if len(tr) > 0:
                        for i in tr:
                            if i.transfer == data['payment_amount']:
                                a = Data(i.id, i.date, i.transfer, i.fee, i.total, i.name)
                                b = Data(data['order_id'], datetime.datetime.date(parser.parse(data['date_created'])),
                                         data['payment_amount'], 0, data['payment_amount'], 'Chocotravel/Aviata')
                                equal.append(a)
                                equal.append(b)
                            else:
                                a = Data(i.id, i.date, i.transfer, i.fee, i.total, i.name)
                                b = Data(data['order_id'], datetime.datetime.date(parser.parse(data['date_created'])),
                                         data['payment_amount'], 0, data['payment_amount'], 'Chocotravel/Aviata')
                                notequal.append(a)
                                notequal.append(b)
            #
            # for i in equal:
            #     print(i.)
            # args = {'form':form, 'transactions': transactions, 'name':name}
            args = {'form':form, 'equal': equal, 'notEqual':notequal}
            return render(request, self.template_name, args)

ids = [1,2,3,4]
names = ['kaspi', 'processing', 'tourism', 'kazkom']

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

# return render(request, 'project/update_list.html', {})

# [
#  {
#   "id" : 471688,
#   "date_created" : 1532401037, дата в таймстамп
#   "order_id" : 1153915,
#   "payment_amount" : 41072.00000,
#   "payment_type" : 1, тип оплаты(1-казком, 5 каспи, и тд. сейчас это не важно, точные ключи я вам позже скину)
#   "payment_reference" : "820581779284",
#   "status" : 1, (1-оплата, 2-возврат)
#   "succeed" : 1
#  },
#  {
#   "id" : 471687,
#   "date_created" : 1532400998,
#   "order_id" : 1153959,
#   "payment_amount" : 3918.00000,
#   "payment_type" : 1,
#   "payment_reference" : "820581779247",
#   "status" : 1,
#   "succeed" : 1
#  },
#  {
#   "id" : 471686,
#   "date_created" : 1532400603,
#   "order_id" : 1153950,
#   "payment_amount" : 25708.00000,
#   "payment_type" : 1,
#   "payment_reference" : "820581778726",
#   "status" : 1,
#   "succeed" : 1
#  },
#  {
#   "id" : 471685,
#   "date_created" : 1532400545,
#   "order_id" : 1153949,
#   "payment_amount" : 7836.00000,
#   "payment_type" : 1,
#   "payment_reference" : "820581778643",
#   "status" : 1,
#   "succeed" : 1
#  },
#  {
#   "id" : 471684,
#   "date_created" : 1532400502,
#   "order_id" : 1153901,
#   "payment_amount" : 30252.00000,
#   "payment_type" : 1,
#   "payment_reference" : "820581778597",
#   "status" : 1,
#   "succeed" : 1
#  },
#  {
#   "id" : 471683,
#   "date_created" : 1532400423,
#   "order_id" : 1153939,
#   "payment_amount" : 142.22000,
#   "payment_type" : 5,
#   "payment_reference" : "22482516447008",
#   "status" : 1,
#   "succeed" : 1
#  },
#  {
#   "id" : 471682,
#   "date_created" : 1532400413,
#   "order_id" : 1153939,
#   "payment_amount" : 142.22000,
#   "payment_type" : 5,
#   "payment_reference" : "22482516447008",
#   "status" : 1,
#   "succeed" : 1
#  },
#  {
#   "id" : 471681,
#   "date_created" : 1532400357,
#   "order_id" : 1153927,
#   "payment_amount" : -108867.00000,
#   "payment_type" : 12,
#   "payment_reference" : "",
#   "status" : 2,
#   "succeed" : 1
#  },
#  {
#   "id" : 471680,
#   "date_created" : 1532400188,
#   "order_id" : 1153940,
#   "payment_amount" : 48033.00000,
#   "payment_type" : 1,
#   "payment_reference" : "820581778206",
#   "status" : 1,
#   "succeed" : 1
#  },
#  {
#   "id" : 471679,
#   "date_created" : 1532400097,
#   "order_id" : 1153933,
#   "payment_amount" : 26308.00000,
#   "payment_type" : 1,
#   "payment_reference" : "820581778101",
#   "status" : 1,
#   "succeed" : 1
#  }
# ]
