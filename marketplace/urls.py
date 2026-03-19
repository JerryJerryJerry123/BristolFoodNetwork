from django.urls import path
from .views import (create_product, 
                    marketplace_home, 
                    products_by_category, 
                    product_detail, 
                    add_to_cart, 
                    view_cart, 
                    update_cart_item,
                    checkout,
                    producer_orders,
                    producer_order_detail,
                    order_history,
                    producer_products,
                    edit_product,
                    write_review)

urlpatterns = [
    path('product/new/', create_product, name='create_product'),

    path('', marketplace_home, name='marketplace_home'),
    path('category/<int:category_id>/', products_by_category, name='products_by_category'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),

    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/update/<int:item_id>/', update_cart_item, name='update_cart_item'),
    
    path('checkout/', checkout, name='checkout'),
    path('producer/orders/', producer_orders, name='producer_orders'),

    path('producer/orders/<int:suborder_id>/',producer_order_detail,name='producer_order_detail'),
    path('orders/', order_history, name='order_history'),

    path("producer/products/", producer_products, name="producer_products"),
    path("producer/products/<int:product_id>/edit/", edit_product, name="edit_product"),

    path("product/<int:product_id>/review/", write_review, name="write_review"),
]