
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('demo/', views.demo_page, name='demo'),
    path('demo/sidebar_content/', views.sidebar_content, name='sidebar_content')
]
