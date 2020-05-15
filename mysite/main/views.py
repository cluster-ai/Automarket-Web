
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.core import serializers
from django.conf import settings

import os
import json
import datetime

#local
from .forms import DemoLogin
from .models import DemoKey, HistoricalData, ApiKey

from .market_data import Historical, init_dir, load_data

#Initializes market_data
init_dir()
Historical.backfill('startup_key', 'KRAKEN_BTC_5MIN')

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


def sidebar_content(request):
	raw_data = HistoricalData.objects.all()
	raw_data = json.loads(serializers.serialize('json', raw_data))

	#converts raw database time value to sidbar table format
	def convert_date(date):
		unix = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.0000000Z')
		unix = int(unix.replace(tzinfo=datetime.timezone.utc).timestamp())
		date = datetime.datetime.utcfromtimestamp(unix)
		return date.strftime("%b %Y")
	
	data = {}
	for item in raw_data:
		exchange_id = item['fields']['exchange_id']
		coin = item['fields']['asset_id_base']
		start = convert_date(item['fields']['data_start'])
		end = convert_date(item['fields']['data_end'])
		#does item exchange exist in data
		if exchange_id not in data:
			#exchange_id does not exist in data
			data.update({exchange_id: []})

		#append currency
		data[exchange_id].append({'coin': coin,
									'start': start,
									'end': end})
	'''
	new data format:
	data = {
		'exchange_1': [
			{
				'coin': 'coin1',
				'start': 'mm/yy',
				'end': 'mm/yy'
			},
			{
				'coin': 'coin1',
				'start': 'mm/yy',
				'end': 'mm/yy'
			},
			{...}
		],
		'Exchange_2': [
			...
		]
	}
	'''

	return HttpResponse(json.dumps(data))