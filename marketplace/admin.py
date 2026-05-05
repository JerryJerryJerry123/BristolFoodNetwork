from django.contrib import admin
from .models import Product, Category, SubOrder

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

@admin.register(SubOrder)
class SubOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "producer",
        "status",
        "delivery_date",
        "subtotal",
    )

    list_filter = ("status", "delivery_date", "producer")
    search_fields = ("order__id", "producer__username")