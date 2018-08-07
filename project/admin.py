# Register your models here.
from django.contrib import admin
from .models import Transaction
from .models import UpdatedTransaction

admin.site.register(Transaction)
admin.site.register(UpdatedTransaction)