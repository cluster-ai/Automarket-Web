from django.contrib import admin

#local
from .models import DemoKey, HistoricalData, ApiKey

# Register your models here.
admin.site.register(DemoKey)
admin.site.register(HistoricalData)
admin.site.register(ApiKey)