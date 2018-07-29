from django import forms

class PostForm  (forms.Form):
    # id = forms.IntegerField()
    # start_date = forms.DateField()
    # end_date = forms.DateField()
    CHOICES = (('Kaspi', 'Kaspi'), ('Nurbank', 'Nurbank'),)
    name = forms.ChoiceField(choices=CHOICES)

class UpdateForm(forms.Form):
    id = forms.IntegerField()

