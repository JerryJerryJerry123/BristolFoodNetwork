from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "producer",
        "category",
        "price",
        "quantity",
        "status",
        "is_surplus",
        "organic_certified",
        "created_at"
    )

    list_filter = (
        "status",
        "is_surplus",
        "organic_certified",
        "category"
    )

    search_fields = (
        "name",
        "description",
        "producer__username"
    )

    ordering = ("-created_at",)