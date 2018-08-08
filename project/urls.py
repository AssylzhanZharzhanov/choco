from django.conf.urls import url
from . import views
from project.views import FormView
from project.views import ParseForm
from  project.views import History
from project.views import Analytics
from login.views import login
from login.views import logout
from login.views import register

urlpatterns = [
    url(r'^$', FormView.as_view(), name='transaction_list'),
    # url('update', ParseForm.as_view(),name='update_list')
    url('history',  History.as_view(), name='History'),
    url('analytics', Analytics.as_view(), name='History'),
    url('auth/login', login),
    url('auth/logout', logout),
    url('auth/register', register),
]