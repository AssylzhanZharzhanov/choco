from django import forms
from project.models import Transaction

class DateInput(forms.DateInput):
    input_type = 'date'

class PostForm  (forms.Form):
    # id = forms.IntegerField()
    # start_date = forms.DateField()
    # end_date = forms.DateField()
    CHOICES = (('Kaspi', 'Kaspi'), ('Nurbank', 'Nurbank'), ('Tourism', 'Tourism'), ('Kazkom', 'Kazkom'))
    name = forms.ChoiceField(choices=CHOICES)


class UpdateForm(forms.Form):
    id = forms.IntegerField()

