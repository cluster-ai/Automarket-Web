from django.shortcuts import render
from django.http import HttpResponse
from .models import Tutorial
from django.contrib.auth.forms import UserCreationForm



def homepage(request):
	return render(request=request, template_name='main/home.html',
				  context={'tutorials': Tutorial.objects.all})

def register(request):
	form = UserCreationForm
	return render(request,
				  'main/register.html',
				  context={'form': form})

def login(request):
	form = UserCreationForm
	return render(request,
				  'main/login.html',
				  context={'form': form})