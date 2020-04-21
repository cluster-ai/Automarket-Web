
from django.shortcuts import render, redirect
from django.contrib import messages

#local
from .forms import DemoLogin
from .models import DemoKey

# Create your views here.

def landing_page(request):
	if request.method == 'POST':
		form = DemoLogin(request.POST)
		if form.is_valid():
			key = form.cleaned_data.get('key')
			try:
				db_val = DemoKey.objects.get(key=key)
				print(db_val)
			except DemoKey.DoesNotExist:
				messages.error(request, f'Invalid Key: {key}')
			else:
				return redirect('main:demo')
	else:
		form = DemoLogin(request.POST)

	return render(request,
				  'main/landing.html',
				  context={'form': form})


def demo_page(request):
	return render(request,
				  'main/demo.html')