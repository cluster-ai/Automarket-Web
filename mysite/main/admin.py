from django.contrib import admin

#local
from .models import DemoKey
from .models import HistoricalData

# Register your models here.
admin.site.register(DemoKey)
admin.site.register(HistoricalData)