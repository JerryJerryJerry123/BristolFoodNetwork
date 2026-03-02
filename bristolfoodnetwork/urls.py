from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    #marketplace
    path('marketplace/', include('marketplace.urls')),
    path('', views.home, name='home'),
    #accounts
    path('', include('accounts.urls')),
]