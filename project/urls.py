from django.conf.urls import url
from . import views
from project.views import FormView
from project.views import ParseForm

urlpatterns = [
    url('transaction', FormView.as_view(), name='transaction_list'),
    url('update', ParseForm.as_view(),name='update_list')
]