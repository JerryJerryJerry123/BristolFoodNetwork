from django import forms
from django.contrib.auth.models import User
from .models import ProducerProfile, CustomerProfile


class ProducerRegistrationForm(forms.ModelForm):
    #user fields
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    #producer creation 
    class Meta:
        model = ProducerProfile
        fields = [
            'business_name',
            'contact_name',
            'phone',
            'address',
            'postcode',
        ]


class CustomerRegistrationForm(forms.ModelForm):
    #user fields
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        #customer setup
        model = CustomerProfile
        fields = [
            'full_name',
            'phone',
            'delivery_address',
            'postcode',
            'account_type'
        ]
        