from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'unit',
            'quantity',
            'status',
            'is_surplus',
            'discount_percentage',
            'organic_certified',
            'allergen_info',
            'harvest_date',
            'category'
        ]