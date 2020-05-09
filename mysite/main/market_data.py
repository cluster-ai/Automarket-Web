
#django
from django.conf import settings
from .models import HistoricalData

#standard libraries
import time
import datetime
import json
import os

#third-party
import numpy as np
import pandas as pd

#defines root directory for market data filesystem
MARKET_DATA_DIR = os.path.join(settings.BASE_DIR, 'main/market_data')

HISTORICAL_DIR = os.path.join(MARKET_DATA_DIR, 'historical')
COINAPI_DIR = os.path.join(MARKET_DATA_DIR, 'coinapi')


def init_dir():
	#makes sure fixed directories all exist (directories)
	###BASE_DIR###
	if os.path.isdir(MARKET_DATA_DIR) == False:
		os.mkdir(MARKET_DATA_DIR)
	###HISTORICAL_DIR###
	if os.path.isdir(HISTORICAL_DIR) == False:
		os.mkdir(HISTORICAL_DIR)
	###COINAPI_DIR###
	if os.path.isdir(COINAPI_DIR) == False:
		os.mkdir(COINAPI_DIR)


def unix_to_date(unix, show_dec=True):
	#the datetime package is only accurate to 6 decimals but 7 are 
	#needed for date format being used. Since the decimal value is 
	#the same regardless of unix or date, I have it copied over
	#from unix and converted to string then added to date between
	#the '.' and 'Z' characters

	#gets the string of int(unix_decimal * 10^7)
	decimal = round((unix % 1 * (10**7)))
	decimal = str(int(decimal))
	#leads decimal with zeros so total digit count is 7
	decimal = decimal.zfill(7)

	#drops the decimal from unix
	unix = int(unix)

	#integer unix value converted to date string
	date = datetime.datetime.utcfromtimestamp(unix)
	date = date.strftime('%Y-%m-%dT%H:%M:%S')

	#decimal string added to datetime
	if show_dec == True:
		date = date + f'.{decimal}Z'

	#return format: 'yyyy-mm-ddTHH:MM:SS.fffffffZ'
	return date


def date_to_unix(date):
	#This function accepts two formats:
	#   "%Y-%m-%dT%H:%M:%" and "%Y-%m-%d"
	if 'T' in date:
		#the datetime package is only accurate to 6 decimals but 7 are 
		#needed for date format being used. Since the decimal value is 
		#the same regardless of unix or date, I have it copied over
		#from date and converted to float then added to unix
		start = date.find('.') + 1 #first decimal value index
		end = date.find('Z') #the index of value that ends decimal string

		#extracts first 7 digits of decimal
		decimal = str(round(float(date[start:end])))

		#new date without decimal
		date = date[0:start-1]

		#date string is converted to datetime value
		unix = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
		#datetime value is converted to unix value in UTC timezone as int
		unix = str(int(unix.replace(tzinfo=datetime.timezone.utc).timestamp()))
		#adds decimal to unix
		unix = float(f'{unix}.{decimal}')
	else:
		#this assumes format is "%Y-%m-%d"
		#date string is converted to datetime value
		unix = datetime.datetime.strptime(date, '%Y-%m-%d')
		#datetime value is converted to unix value in UTC timezone as int
		unix = unix.replace(tzinfo=datetime.timezone.utc).timestamp()

	return unix


def historical(index_id, start_time=None, end_time=None):
	'''
	Returns dataframe for the specified historical data

	Parameters:
		index_id   : (str) id to desired historical data

		start_time : (int, unix-utc) returned data
					 will be >= this time
			NOTE: if start_time == None, all data before
				  end_time is returned

		end_time   : (int, unix-utc) returned data
					 will be <= this time
			NOTE: if end_time == None, all data after
				  start_time is returned

	NOTE: start_time parameter uses 'time_period_start' column
		  as reference. end_time uses 'time_period_end'
	'''

	#loads index data from django model for given index_id
	index_data = HistoricalData.objects.get(index_id=index_id)

	#loads all data from file
	data = pd.read_csv(f'{HISTORICAL_DIR}/{index_data.filepath}')

	#makes data.index equal to 'time_period_start' column
	data.set_index('time_period_start', drop=False, inplace=True)

	#slices data based on start_time if parameter was given
	if start_time != None:
		#catches out out of scope start_time
		if start_time not in data.index:
			raise IndexError(f'{start_time} index not in {index_data.filename}')
		data = data.loc[start_time: , :]

	#slices data based on end_time if parameter was given
	if end_time != None:
		#catches out out of scope end_time
		if end_time not in data.index:
			raise IndexError(f'{end_time} index not in {index_data.filename}')
		data = data.loc[:end_time, :]

	return data
	