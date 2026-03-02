from django.urls import path
from .views import (create_product, 
                    marketplace_home, 
                    products_by_category, 
                    product_detail, 
                    add_to_cart, 
                    view_cart, 
                    update_cart_item)

urlpatterns = [
    path('product/new/', create_product, name='create_product'),

    path('', marketplace_home, name='marketplace_home'),
    path('category/<int:category_id>/', products_by_category, name='products_by_category'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),

    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/update/<int:item_id>/', update_cart_item, name='update_cart_item'),
]