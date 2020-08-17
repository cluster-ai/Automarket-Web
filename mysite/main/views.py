
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core import serializers
from django.conf import settings

import os
import json
import datetime

#local
from .forms import DemoLogin
from .models import DemoKey, HistoricalData, ApiKey

from .market_data import Historical, init_dir

#Initializes market_data
#Historical.backfill('startup_key', 'COINBASE_BTC_5MIN')

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


def control_box(request):
	if request.method == 'POST':
		index_id = request.POST.get('index_id')

		#NOT IDEAL, loads entire file and grabs column names
		df = Historical.load_data(index_id)
		#extracts columns and converts pd.index to list
		columns = df.columns.tolist()

		#removes columns that are not applicable to a line graph
		return_columns = []
		for col in columns:
			if "time" in col:
				continue
			elif "isnan" == col:
				continue
			else:
				return_columns.append(col)

		return JsonResponse({'columns': return_columns})
	else:
		return JsonResponse({"nothing to see": "this isn't happening"})


def sidebar(request):
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

		#items being sent
		index_id = item['fields']['index_id']
		coin = item['fields']['asset_id_base']
		start = convert_date(item['fields']['data_start'])
		end = convert_date(item['fields']['data_end'])

		#does item exchange exist in data
		if exchange_id not in data:
			#exchange_id does not exist in data
			data.update({exchange_id: []})

		#append currency
		data[exchange_id].append({
			'index_id': index_id,
			'coin': coin,
			'start': start,
			'end': end
		})
	'''
	new data format:
	data = {
		'exchange_1': [
			{
				'index_id': 'KRAKEN_BTC_5MIN',
				'coin': 'coin1',
				'start': 'mm/yy',
				'end': 'mm/yy'
			},
			{
				'index_id': 'KRAKEN_ETH_5MIN',
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

	return JsonResponse(data)


def historical_index(request):
	if request.method == 'POST':
		index_id = request.POST.get('index_id')

		raw_data = HistoricalData.objects.filter(index_id=index_id)
		data = json.loads(serializers.serialize('json', raw_data))[0]

		return JsonResponse(data['fields'])
	else:
		return JsonResponse({"nothing to see": "this isn't happening"})


def market_data(request):
	'''
	POST data:
		index_id (str) - id of market data in historical database
		columns (list(str)) - list of desired columns

	returns:
		data (list) - df.to_json(orient="values")
		column_indexes (dict) - list index of selected_columns in df_columns
	'''
	if request.method == 'POST':
		selected_columns = request.POST.getlist('columns[]')
		index_id = request.POST.get('index_id')
		print(index_id)
		print(selected_columns)

		# Loads market data from database
		df = Historical.load_data(index_id).head(5)
		df_columns = list(df.columns)
		df_values = df.to_json(orient="values")
		print('\n\ndf_values:', df_values)

		# generates dict of requested columns and index
		# EX: {'column1': columns_index(int), ...}
		column_indexes = {}
		for col in selected_columns:
			column_indexes.update({col: df_columns.index(col)})

		return JsonResponse({
			'data': [0,1,2,3],
			'column_indexes': column_indexes,
		})
	else:
		return JsonResponse({"nothing to see": "this isn't happening"})