from django.db import models


class DemoKey(models.Model):
	key = models.CharField(max_length=50)

	def __str__(self):
		return self.key

	class Meta:
		verbose_name_plural = 'Demo Keys'


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

'''
class HistoricalData(models.Model):
	index_id = models.CharField(max_length=100)
	symbol_id = models.CharField(max_length=100)
	exchange_id = models.CharField(max_length=100)
	asset_id_quote = models.CharField(max_length=100)
	asset_id_base = models.CharField(max_length=100)
	period_id = models.CharField(max_length=100)
	time_increment = models.PositiveIntegerField()
	data_points = models.PositiveIntegerField()
	data_start = models.CharField(max_length=100)
	data_end = models.CharField(max_length=100)

	def __str__(self):
		return self.index_id

	class Meta:
		verbose_name_plural = "Historical Index"


class HistoricalData(models.Model):
	index = models.OneToOneField(
		HistoricalIndex,
		on_delete=models.CASCADE,
		primary_key=False
	)
	time_period_start = models.PositiveIntegerField()
	time_period_end = models.PositiveIntegerField()
	price_high = models.PositiveIntegerField()
	price_low = models.PositiveIntegerField()
	price_open = models.PositiveIntegerField()
	price_close = models.PositiveIntegerField()
	volume_traded = models.PositiveIntegerField()
	trades_count = models.PositiveIntegerField()
	market_cap = models.PositiveIntegerField()
	is_nan = models.BooleanField()

	def __str__(self):
		return self.index.index_id

	class Meta:
		verbose_name_plural = "Historical Data"
	'''