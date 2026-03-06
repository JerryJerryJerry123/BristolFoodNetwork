from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    #register button
    path('register/', views.register, name='register'),
    #redirects to specific (placeholder)
    path('register/producer/', views.register_producer, name='register_producer'),
    path('register/customer/', views.register_customer, name='register_customer'),
    # Login / Logout using Django built-in views 
    path( 'login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login' ), 
        path(
        'logout/',
        auth_views.LogoutView.as_view(
            next_page='/',
        ),
        name='logout'
    ),
    # Payments and Producer Weekly Settlement Payments
    path('payments/',  views.payments, name='payments'),
    path('payments/weekly_settlement_payments/',  views.producer_weekly_settlement_payments, name='producer_weekly_settlement_payments'),

]