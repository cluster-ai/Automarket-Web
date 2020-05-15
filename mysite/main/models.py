from django.db import models


class DemoKey(models.Model):
	key = models.CharField(max_length=50)

	def __str__(self):
		return self.key

	class Meta:
		verbose_name_plural = 'Demo Keys'

'''
class TrackedExchange(models.Model):
	exchange_id = models.CharField(max_length=200)
'''


class HistoricalData(models.Model):
	index_id = models.CharField(max_length=200)
	file_name = models.CharField(max_length=200)
	file_path = models.CharField(max_length=200)
	symbol_id = models.CharField(max_length=200)
	exchange_id = models.CharField(max_length=200)
	asset_id_quote = models.CharField(max_length=200)
	asset_id_base = models.CharField(max_length=200)
	period_id = models.CharField(max_length=200)
	time_increment = models.PositiveIntegerField()
	data_points = models.PositiveIntegerField()
	data_start = models.CharField(max_length=200)
	data_end = models.CharField(max_length=200)

	def __str__(self):
		return self.index_id

	class Meta:
		verbose_name_plural = 'Historical Data'


class ApiKey(models.Model):
	name = models.CharField(max_length=200, default=1)
	key = models.CharField(max_length=200)
	limit = models.PositiveIntegerField()
	remaining = models.PositiveIntegerField()
	reset = models.CharField(max_length=200)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'API Keys'