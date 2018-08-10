# Register your models here.
from django.contrib import admin
from .models import Transaction
from .models import UpdatedTransaction
from .models import Task


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'time','name','transfer','fee','total','company','updated','update_time','reference')
    list_filter = ('date','time')
    search_fields = ('id',)


class UpdatedTransactionAdmin(admin.ModelAdmin):
    list_display = ('ids', 'date', 'update_date', 'time','update_time' ,'name','transfer','fee','total','company','reference', 'fixed')
    list_filter = ('date','time')
    search_fields = ('ids',)

class TasksTransaction(admin.ModelAdmin):
    list_display = ('user', 'ids', 'date', 'time','transfer','fee','total','reference','name','status', 'comment')
    list_filter = ('date', 'time')
    search_fields = ('user', 'ids')

admin.site.register(Transaction,TransactionAdmin)
admin.site.register(UpdatedTransaction, UpdatedTransactionAdmin)
admin.site.register(Task, TasksTransaction)
