from django.urls import path
from .views import financial_report

urlpatterns = [
    path('reports', financial_report, name='financial_report'),
]
