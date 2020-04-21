
from django import forms

#local
from .models import DemoKey

#example form
class NameForm(forms.Form):
	your_name = forms.CharField(label='Your name', max_length=100)


class DemoLogin(forms.Form):
	key = forms.CharField(label='Demo Key', 
						  max_length=50,
						  required=True)