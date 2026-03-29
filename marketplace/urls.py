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
                    write_review,
                    reorder,
                    update_suborder_status,
                    mark_ready,
                    mark_delivered,
                    recurring_orders,
                    edit_scheduled_order,
                    content,
                    view_content,
                    cancel_suborder
                    )


urlpatterns = [
    path('content/', content, name='content'),
    path('view-content/', view_content, name='view_content'),

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
    path('order/<int:order_id>/reorder/', reorder, name='reorder'),

    path("producer/products/", producer_products, name="producer_products"),
    path("producer/products/<int:product_id>/edit/", edit_product, name="edit_product"),

    path("product/<int:product_id>/review/", write_review, name="write_review"),
    path("producer/orders/<int:suborder_id>/status/", update_suborder_status, name="update_suborder_status"), 
    path("producer/orders/<int:suborder_id>/ready/",mark_ready,name="mark_ready"),
    path("producer/orders/<int:suborder_id>/delivered/", mark_delivered, name="mark_delivered"),
    path("orders/<int:suborder_id>/cancel/", cancel_suborder, name="cancel_suborder"),
    path("recurring/", recurring_orders, name="recurring_orders"),
    path('scheduled/<int:order_id>/edit/', edit_scheduled_order, name='edit_scheduled_order'),

]