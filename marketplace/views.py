from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from django.db.models import Q

from accounts.models import CustomerProfile
from .forms import ProductForm
from .models import Product, Category, Cart, CartItem

from django.utils import timezone
from datetime import timedelta
from collections import defaultdict

from .models import (
    Product,
    Category,
    Cart,
    CartItem,
    Order,
    SubOrder,
    OrderItem
)
#login requirements
@login_required
def create_product(request):

    #only producers!
    if not hasattr(request.user, 'producerprofile'):
        return redirect('/')

    if request.method == 'POST':
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save(commit=False)
            product.producer = request.user
            product.save()

            return redirect('/')

    else:
        form = ProductForm()

    return render(request,
                  'marketplace/create_product.html',
                  {'form': form})

def marketplace_home(request):
    categories = Category.objects.all().order_by("name")

    q = request.GET.get("q", "").strip()

    products = Product.objects.all().select_related("category", "producer").order_by("-created_at")

    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(allergen_info__icontains=q)
        )

    return render(request, "marketplace/home.html", {
        "categories": categories,
        "products": products,
        "q": q,
    })

def products_by_category(request, category_id):
    categories = Category.objects.all().order_by("name")

    q = request.GET.get("q", "").strip()

    category = get_object_or_404(Category, id=category_id)

    products = Product.objects.filter(category=category)\
                              .select_related("category", "producer")\
                              .order_by("-created_at")

    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(allergen_info__icontains=q)
        )

    return render(request, "marketplace/category.html", {
        "categories": categories,
        "category": category,
        "products": products,
        "q": q,
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related("producer", "category"), id=product_id)

    allergens = product.allergen_info or []

    if isinstance(allergens, str):
        allergens = [allergens]

    return render(request, "marketplace/product_detail.html", {
        "product": product,
        "allergens": allergens,
    })

def _get_customer_cart(user):
    customer = CustomerProfile.objects.get(user=user)
    cart, _ = Cart.objects.get_or_create(customer=customer)
    return cart

@login_required
def add_to_cart(request, product_id):
    if not hasattr(request.user, "customerprofile"):
        return redirect("/")

    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        qty_str = request.POST.get("quantity", "1").strip()

        try:
            qty = Decimal(qty_str)
            if qty <= 0:
                raise ValueError()
        except Exception:
            messages.error(request, "Please enter a valid quantity.")
            return redirect("product_detail", product_id=product.id)

        cart = _get_customer_cart(request.user)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if created:
            item.quantity = qty
        else:
            item.quantity = item.quantity + qty

        item.save()
        messages.success(request, f"Added {product.name} to your cart.")

    return redirect("product_detail", product_id=product.id)

@login_required
def view_cart(request):
    if not hasattr(request.user, "customerprofile"):
        return redirect("/")

    cart = _get_customer_cart(request.user)

    return render(request, "marketplace/cart.html", {
        "cart": cart,
    })

@login_required
def update_cart_item(request, item_id):
    if not hasattr(request.user, "customerprofile"):
        return redirect("/")

    cart = _get_customer_cart(request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if request.method == "POST":
        qty_str = request.POST.get("quantity", "").strip()

        try:
            qty = Decimal(qty_str)
        except Exception:
            messages.error(request, "Please enter a valid quantity.")
            return redirect("view_cart")

        if qty <= 0:
            item.delete()
            messages.success(request, "Item removed from cart.")
        else:
            item.quantity = qty
            item.save()
            messages.success(request, "Cart updated.")

    return redirect("view_cart")

@login_required
def checkout(request):
    if not hasattr(request.user, "customerprofile"):
        return redirect("/")

    cart = _get_customer_cart(request.user)
    cart_items = cart.items.select_related("product__producer")

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("view_cart")

    if request.method == "POST":

        # -----------------------------
        # PAYMENT VALIDATION
        # -----------------------------
        payment_method = request.POST.get("payment_method")

        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return render(request, "marketplace/checkout.html", {
                "cart": cart
            })

        if payment_method == "card":
            card_number = request.POST.get("card_number", "").strip()
            expiry = request.POST.get("expiry", "").strip()
            cvv = request.POST.get("cvv", "").strip()

            if not card_number or not expiry or not cvv:
                messages.error(request, "Please enter card details.")
                return render(request, "marketplace/checkout.html", {
                    "cart": cart
                })
        
        # -----------------------------
        # STOCK VALIDATION
        # -----------------------------
        for item in cart_items:
            if item.quantity > item.product.quantity:
                messages.error(request, f"Not enough stock for {item.product.name}")
                return render(request, "marketplace/checkout.html", {
                    "cart": cart
                })

        # -----------------------------
        # CREATE ORDER
        # -----------------------------
        order = Order.objects.create(
            customer=request.user.customerprofile
        )

        grouped_items = defaultdict(list)

        # Group items by producer
        for item in cart_items:
            grouped_items[item.product.producer].append(item)

        total_amount = 0
        minimum_date = timezone.now() + timedelta(hours=48)

        for producer, items in grouped_items.items():

            delivery_date_str = request.POST.get(f"delivery_date_{producer.id}")

            if not delivery_date_str:
                messages.error(request, "Please select a delivery date.")
                return render(request, "marketplace/checkout.html", {
                    "cart": cart
                })

            delivery_date = timezone.datetime.fromisoformat(delivery_date_str).date()

            if delivery_date < minimum_date.date():
                messages.error(request, "Delivery must be at least 48 hours from now.")
                return render(request, "marketplace/checkout.html", {
                    "cart": cart
                })

            suborder = SubOrder.objects.create(
                order=order,
                producer=producer,
                delivery_date=delivery_date,
            )

            subtotal = 0

            for item in items:

                OrderItem.objects.create(
                    suborder=suborder,
                    product=item.product,
                    quantity=item.quantity
                )

                item.product.quantity -= item.quantity
                item.product.save()

                subtotal += item.line_total

            suborder.subtotal = subtotal
            suborder.save()

            total_amount += subtotal

        order.total_amount = total_amount
        order.save()

        # Clear cart
        cart.items.all().delete()

        messages.success(request, "Order placed successfully!")
        return redirect("/")

    return render(request, "marketplace/checkout.html", {
        "cart": cart
    })

from .models import SubOrder

@login_required
def producer_orders(request):
    # Only producers allowed
    if not hasattr(request.user, "producerprofile"):
        return redirect("/")

    # Get suborders belonging to this producer
    suborders = SubOrder.objects.filter(
        producer=request.user
    ).select_related(
        "order", "order__customer", "order__customer__user"
    ).prefetch_related(
        "items__product"
    ).order_by("delivery_date")

    return render(request, "marketplace/producer_orders.html", {
        "suborders": suborders
    })

@login_required
def producer_order_detail(request, suborder_id):
    if not hasattr(request.user, "producerprofile"):
        return redirect("/")

    suborder = get_object_or_404(
        SubOrder.objects.select_related(
            "order",
            "order__customer",
            "order__customer__user"
        ).prefetch_related("items__product"),
        id=suborder_id,
        producer=request.user
    )

    return render(request, "marketplace/producer_order_detail.html", {
        "suborder": suborder
    })

@login_required
def order_history(request):
    # Get the customer profile for the logged-in user
    customer_profile = CustomerProfile.objects.get(user=request.user)

    # Get all orders for this customer, most recent first
    orders = Order.objects.filter(customer=customer_profile).order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'marketplace/order_history.html', context)