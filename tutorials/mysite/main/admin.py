from django.contrib import admin
from .models import Tutorial, TutorialSeries, TutorialCategory

# Register your models here.

admin.site.register(Tutorial)
admin.site.register(TutorialSeries)
admin.site.register(TutorialCategory)