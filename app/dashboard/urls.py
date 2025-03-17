# dashboard/urls.py
from django.urls import path
from .views import dashboard, import_csv

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('import_csv/', import_csv, name='import_csv'),
]
