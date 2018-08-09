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
    list_display = ('ids', 'date', 'time','name','transfer','fee','total','company','update_time','reference')
    list_filter = ('date','time')
    search_fields = ('ids',)


admin.site.register(Transaction,TransactionAdmin)
admin.site.register(UpdatedTransaction, UpdatedTransactionAdmin)
admin.site.register(Task)

