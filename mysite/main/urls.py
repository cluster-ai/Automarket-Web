
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('demo/', views.demo_page, name='demo'),
    path('demo/sidebar/', views.sidebar, name='sidebar'),
    path('demo/display_box/', views.display_box, name='display_box')
]
