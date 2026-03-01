from django.urls import path
from .views import create_product

urlpatterns = [
    path('product/new/', create_product, name='create_product'),
]