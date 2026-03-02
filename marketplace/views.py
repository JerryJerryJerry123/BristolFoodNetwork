from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from django.db.models import Q

from accounts.models import CustomerProfile
from .forms import ProductForm
from .models import Product, Category, Cart, CartItem

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