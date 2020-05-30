
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('demo/', views.demo_page, name='demo'),
    path('demo/sidebar/', views.sidebar, name='sidebar'),
    path('demo/control_box/', views.control_box, name='control_box')
]
