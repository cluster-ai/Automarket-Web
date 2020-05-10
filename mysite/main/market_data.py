
#django
from django.conf import settings
from .models import HistoricalData, ApiKey

#standard libraries
import time
import datetime
import json
import os
from string import Template

#third-party
import numpy as np
import pandas as pd

#defines root directory for market data filesystem
MARKET_DATA_DIR = os.path.join(settings.BASE_DIR, 'main/market_data')

HISTORICAL_DIR = os.path.join(MARKET_DATA_DIR, 'historical')
COINAPI_DIR = os.path.join(MARKET_DATA_DIR, 'coinapi')
COIN_INDEX_PATH = os.path.join(COINAPI_DIR, 'coin_index.json')


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
	data = pd.read_csv(f'{HISTORICAL_DIR}/{index_data.file_path}')

	#makes data.index equal to 'time_period_start' column
	data.set_index('time_period_start', drop=False, inplace=True)

	#slices data based on start_time if parameter was given
	if start_time != None:
		#catches out out of scope start_time
		if start_time not in data.index:
			raise IndexError(f'{start_time} index not in {index_data.file_name}')
		data = data.loc[start_time: , :]

	#slices data based on end_time if parameter was given
	if end_time != None:
		#catches out out of scope end_time
		if end_time not in data.index:
			raise IndexError(f'{end_time} index not in {index_data.file_name}')
		data = data.loc[:end_time, :]

	return data


class Historical():
	base_url = 'https://rest.coinapi.io/v1/'
	#base url for coinapi.io requests

	#url_extensions for various historical requests
	historical_url = Template(base_url + 'ohlcv/${symbol_id}/history')
	period_url = base_url + 'ohlcv/periods'
	exchange_url = base_url + 'exchanges'
	coin_url = base_url + 'symbols'

	#constant
	asset_id_quote = 'USD'


	def update_key(key_id, headers=None):
		'''
		Updates the X-RateLimit-[limit, remaining, reset] data in 
		Database for specified key. Does not update if X-RateLimit-Reset 
		if not greater than existing.

		Parameters:
			- key_id  : (str) user given id to each coinapi api-key
							  used to access api_index in database
			- headers : (dict) request.headers from latest request
		NOTE: If headers are not given, api_id is updated based on
			the last X-RateLimit_Reset time
		'''

		#the current stored api information in database
		key_index = ApiKey.objects.get(name=key_id)

		if headers == None:
			#the unix value of key_index['reset']
			unix_reset = date_to_unix(key_index.reset)

			#if no header given
			if unix_reset <= time.time():
				#reset key_inex['remaining'] information in database
				ApiKey.objects.filter(name=key_id).update(remaining=key_index.limit)
		else:
			#headers given from new request
			for header, value in headers.items():
				#if a header matches, update that value in database
				if 'limit' in header:
					ApiKey.objects.filter(name=key_id).update(limit=value)
				elif 'remaining' in header:
					ApiKey.objects.filter(name=key_id).update(remaining=value)
				elif 'reset' in header:
					ApiKey.objects.filter(name=key_id).update(reset=value)


	def add_item(exchange_id, coin_id, period_id, time_increment):
		'''
		Adds historical item to Database.historical_index

		Parameters:
			exchange_id    : (str) name of exchange in bold: 'KRAKEN'
			coin_id        : (str) crytpocurrency id: 'BTC'
			time_increment : (int) time increment of data in seconds
						  - val must be supported by coinapi period_id
		'''

		#generates index_id using define.py index_id function
		index_id = create_index_id(exchange_id, coin_id, period_id)

		#stops function if item already found in historical_index
		if HistoricalData.objects.filter(index_id=index_id).exists():
			print(f'NOTICE: {index_id} already in historical index')
			return None

		#the first dir is the period_id associated to time_increment
		file_path = Database.historical_dir + f'/{period_id}'
		if os.path.isdir(file_path) == False:
			os.mkdir(file_path)
		#the final dir is the coin_id
		file_path += f'/{exchange_id}'
		if os.path.isdir(file_path) == False:
			os.mkdir(file_path)

		#loads coin_data for new index_item
		data = pd.read_csv(COIN_INDEX_PATH)
		coin_data = None
		for index_item in data:
			if index_item['exchange_id'] == exchange_id:
				#exchange and coin matches
				coin_data = index_item
				break

		#filename-example: 'KRAKEN_BTC_5MIN.csv'
		file_name = f'{index_id}.csv'
		file_path = file_path + f'/{file_name}' #adds filename to dir
		#creates file if there is none
		if os.path.exists(file_path) == False:
			open(file_path, 'w')

		#create new historical data object
		new_item = HistoricalData.objects.create(index_id='index_id')
		#fills out required information
		new_item.filename = file_name
		new_item.file_path = file_path,
		new_item.symbol_id = coin_data['symbol_id']
		new_item.exchange_id = exchange_id
		new_item.asset_id_quote = coin_data['asset_id_quote']
		new_item.asset_id_base = coin_data['asset_id_base']
		new_item.period_id = period_id
		new_item.time_increment = time_increment
		new_item.datapoints = 0
		new_item.data_start = coin_data['data_start']
		new_item.data_end = coin_data['data_start']#not a typo\
		#saves changes to file
		new_item.save()

		print(f'Added {index_id} to Historical Data...')


	def request(cls, key_id, url='', queries={}, 
				filters={}, remaining=False):
		'''
		Parameters:
			url_ext   : (str) is added to Coinapi.base_url in request
			key_id    : (str) name of the api_key being used
			queries   : (dict) a premade dict of params for the request
			filters   : (dict) dict of filters that need to be passed
							 for data to be added to filtered
			remaining : (bool) returns remaining instead of filtered if True

		queries example: {
			'time_start': '2018-02-15T12:53:50.0000000Z',
			'limit': 100,
			'period_id': 'KRAKEN_BTC_5MIN'
		}
		'''

		#update api key index in database
		cls.update_key(key_id)

		#creates a local api index with only "key_id" data 
		key_index = ApiKey.objects.get(name=key_id)

		try:
			print("\nMaking API Request at:", url)
			response = requests.get(url, headers=key_index.api_key, 
									params=queries)
			# If the response was successful, no Exception will be raised
			response.raise_for_status()
		except HTTPError as http_err:
			#catches http errors
			print(f'{http_err}')
			raise ValueError('HTTPError: Killing Process')
		except requests.ConnectionError as connection_err:
			#no connection to internet/coinapi.io
			print(f'{connection_err}')
			raise requests.ConnectionError('HTTP Connection Error')
		except Exception as err:
			#catches any other exceptions
			print(f'{err}')
			raise Exception(f'Exception Occured During HTTP Request')
		else:
			print(f'API Request Successful: code {response.status_code}')
			
			#updates key_index rate limit information in database 
			cls.update_key(key_id, response.headers)

			#converts response to json
			response = response.json()

			#response is converted to json and filtered
			if filters != {}:
				response = cls.filter(response, filters, remaining)
			else:
				print('NOTICE: no filter')

			print()#spacer

			return response


	def backfill(cls, key_id, index_id, limit=None):
		'''
		backfills historical data for specified index_id 
		and saves it to database

		Parameters:
			key_id   : (str) name of the api key being used
			index_id : (dict) historical_index of item being requested
			limit    : (int) request limit set by user
		return: (pd.DataFrame) the data that was requested
		'''

		print('\nBackfilling Historical Data')
		init_time = time.time()

		#updates specified api key
		cls.update_key(key_id)

		#loads the api key information
		key_index = ApiKey.objects.get(name=key_id)
		#loads historical index of data being requested
		hist_index = HistoricalData.objects.get(index_id=index_id)
		#loads start time for request
		time_start = date_to_unix(hist_index.data_end)#unix time
		#loads the end time for request (latest increment time value)
		remainder = init_time % hist_index.time_increment
		time_end = init_time - remainder

		#verifies given limit is valid
		if limit < 0:
			#limit is negative
			raise ValueError(f'limit cannot be negative')
		elif isinstance(limit, int) == False:
			#limit is not an int
			limit_tp = type(limit)
			raise ValueError(f'limit cannot be {limit_tp}, must be int')
		elif limit > key_index.remaining:
			#given limit is larger than remaining requests for key_id
			print('WARNING: given limit exceeds available requests')
			limit = key_index.remaining

		#generates request parameters
		queries = {
			'limit': limit,
			'time_start': unix_to_date(time_start),
			'time_end': unix_to_date(time_end),
			'period_id': hist_index.period_id
		}

		#load url
		url = cls.historical_url.substitute(
					symbol_id=hist_index.symbol_id)

		#make the api request
		response = cls.request(key_id, url=url, queries=queries)
		#converts response to pandas dataframe
		df = pd.DataFrame.from_dict(response.json(), 
										  orient='columns')

		#verifies df has data and converts dates to unix
		if df.empty == False:
			#df is not empty
			#
			#convertes time_period_start to unix values
			print('converting timestamps to unix')

			#iterates each row
			for index, row in df.iterrows():
				#iterates each column
				for col in df.columns:

					if 'time' in col:
						#current column has a time value
						#
						#converts date to unix
						df.at[index, col] = date_to_unix(row[col])

			#calculates price_average column
			price_low = df.loc[:, 'price_low'].values
			price_high = df.loc[:, 'price_high'].values
			price_average = np.divide(np.add(price_low, price_high), 2)
		else:
			#no data in response (df)
			print(f'NOTICE: request has no data')

			columns = {
				'price_close',
				'price_high',
				'price_low',
				'price_open',
				'time_close',
				'time_open',
				'time_period_end',
				'time_period_start',
				'trades_count',
				'volume_traded'
			}

			#re-initializes df with columns
			df = pd.DataFrame(columns=columns)
			price_average = np.nan

		#inserts price_average into df at column index = 2
		df.insert(2, 'price_average', price_average)
		#initializes isnan with False for every row with data
		df['isnan'] = False
		#sets index of df to equal 'time_period_start'
		df.set_index('time_period_start', inplace=True, drop=False)

		#creates an empty dataframe (full_df) with no missing 
		#indexes, start and end times match request queries
		datapoints = (time_end - time_start) / hist_index.time_increment
		index = range(datapoints) + time_start
		full_df = pd.DataFrame(columns=df.columns, index=index)

		#load time_period_start data into column
		full_df['time_period_start'] = full_df.index
		#load time_period_end data into column
		full_df['time_period_end'] = np.add(historical.index,
											   hist_index.time_increment)
		#apply df data to full_df
		full_df.update(df)
		#set empty rows to isnan = True
		new_df.isnan.fillna(True, inplace=True)

		#load existing data from database
		existing_data = historical(index_id)
		#combine existing data and historical
		full_df = existing_data.append(full_df)

		#saves new data to file
		full_df.to_csv(filepath, index=False)

		#updates hist_index
		hist_index.datapoints = len(full_df.index)
		hist_index.data_end = unix_to_date(time_end)
		#commits changes to database
		hist_index.save(update_fields=['datapoints', 'data_end'])

		print(f'\nDuration:', time.time() - init_time)
		print('----------------------------------------------------')


	def reload_coins(cls, key_id):
		'''
		Parameters:
			key_id : (str) name of api_key to use for request

		reloads index of all coins offered by coinapi.io in USD
		organized by coin_id

		Example coin_index.json: {
			'BTC' : {
				'exchanges' : ['KRAKEN', 'BINANCE', ...],
				...
			},
			...
		}
		'''
		print('\nReloading Coin Index...')
		init_time = time.time()

		#requests all currency data and filters by USD
		response = request(key_id, url=cls.coin_url,
								   filters={'asset_id_quote': 'USD'})

		#sets index to empty dict
		coin_index = {}

		#iterates through coins and adds them to coin_index by exchange
		#if exchanges are added as needed
		for item_index in response:

			#loads coin_id from item_index
			coin_id = item_index['asset_id_base']

			#determines if exchange exists in coin_index
			if coin_id not in coin_index:
				#coin_id not found in coin_index
				#
				#creates new coin and adds it to coin_index
				coin_index.update({coin_id: []})
			
			#adds item_index to coin_index
			coin_index[coin_id].append(item_index)

		#saves coin_index to file
		if os.path.exists(COIN_INDEX_PATH) == False:
			open(COIN_INDEX_PATH, 'w')

		with open(COIN_INDEX_PATH, 'w') as file:
			json.dump(coin_index, file, indent=4)

		print(f'Duration:', (time.time() - init_time))
		print('----------------------------------------------------')