from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from django.db.models import Q

from accounts.models import CustomerProfile
from .forms import ProductForm
from .models import Product, Category, Cart, CartItem

from django.utils import timezone
from datetime import timedelta, date
from collections import defaultdict
from django.db.models import Avg

from .models import (
    Product,
    Category,
    Cart,
    CartItem,
    Order,
    SubOrder,
    OrderItem,
    Review,
    RecurringOrder,
    RecurringOrderItem,
    ScheduledOrder,
    ScheduledOrderItem,
    Recipe,
    FarmStory
)

def view_content(request):
    recipes = Recipe.objects.all().order_by("-created_at")
    stories = FarmStory.objects.all().order_by("-created_at")

    return render(request, "marketplace/view_content.html", {
        "recipes": recipes,
        "stories": stories,
    })

@login_required
def content(request):
    producer = request.user

    if request.method == "POST":
        # Add recipe
        if "add_recipe" in request.POST:
            title = request.POST.get("recipe_title")
            description = request.POST.get("recipe_description")
            cooking_instructions = request.POST.get("cooking_instructions")
            season = request.POST.get("season")
            ingredients_ids = request.POST.getlist("ingredients")

            recipe = Recipe.objects.create(
                producer=producer,
                title=title,
                description=description,
                cooking_instructions=cooking_instructions,
                season=season,
            )
            if ingredients_ids:
                recipe.ingredients.set(Product.objects.filter(id__in=ingredients_ids))
            return redirect("content")

        # Delete recipe
        if "delete_recipe" in request.POST:
            recipe_id = request.POST.get("recipe_id")
            recipe = get_object_or_404(Recipe, id=recipe_id, producer=producer)
            recipe.delete()
            return redirect("content")

        # Add farm story
        if "create_story" in request.POST:
            title = request.POST.get("story_title")
            content_text = request.POST.get("story_content")
            harvest_season = request.POST.get("harvest_season")
            FarmStory.objects.create(
                producer=producer,
                title=title,
                content=content_text,
                harvest_season=harvest_season
            )
            return redirect("content")

        # Delete farm story
        if "delete_story" in request.POST:
            story_id = request.POST.get("story_id")
            story = get_object_or_404(FarmStory, id=story_id, producer=producer)
            story.delete()
            return redirect("content")

    # Get data for this producer
    recipes = Recipe.objects.filter(producer=producer).order_by("-created_at")
    stories = FarmStory.objects.filter(producer=producer).order_by("-created_at")
    products = Product.objects.filter(producer=producer)

    return render(request, "marketplace/content.html", {
        "recipes": recipes,
        "stories": stories,
        "products": products,
    })

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

    products = Product.objects.filter(quantity__gt=0).select_related("category", "producer").order_by("-created_at")

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
    product = get_object_or_404(
        Product.objects.select_related("producer", "category"),
        id=product_id
    )

    allergens = product.allergen_info or []

    if isinstance(allergens, str):
        allergens = [allergens]

    # ✅ GET REVIEWS
    reviews = product.reviews.all().order_by("-created_at")

    # ✅ CHECK IF USER IS CUSTOMER (FIXES BUTTON ISSUE)
    is_customer = hasattr(request.user, "customerprofile")

    # ✅ AVERAGE RATING (for case study step 11)
    avg_rating = product.reviews.aggregate(Avg("rating"))["rating__avg"]

    return render(request, "marketplace/product_detail.html", {
        "product": product,
        "allergens": allergens,
        "reviews": reviews,
        "is_customer": is_customer,
        "avg_rating": avg_rating,
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

def get_next_weekday(target_weekday):
    today = date.today()
    days_ahead = target_weekday - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)

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

        
        # PAYMENT VALIDATION
  
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

    
        # STOCK VALIDATION
    
        for item in cart_items:
            if item.quantity > item.product.quantity:
                messages.error(request, f"Not enough stock for {item.product.name}")
                return render(request, "marketplace/checkout.html", {
                    "cart": cart
                })

  
        # CREATE ORDER
 
        # CREATE ORDER

        special_instructions = ""

        if request.user.customerprofile.account_type == "organisation":
            special_instructions = request.POST.get("special_instructions", "")

        order = Order.objects.create(
            customer=request.user.customerprofile,
            special_instructions=special_instructions
        )
        
        grouped_items = defaultdict(list)

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

  
        # RECURRING ORDER 
 
        if request.POST.get("recurring"):

            next_order_date = get_next_weekday(0)  # Monday

            recurring = RecurringOrder.objects.create(
                customer=request.user,
                frequency=request.POST.get("frequency", "weekly"),
                day_of_week="Monday",
                delivery_day="Wednesday",
                next_order_date=next_order_date
            )

            for item in cart_items:
                RecurringOrderItem.objects.create(
                    recurring_order=recurring,
                    product=item.product,
                    quantity=item.quantity
                )

            scheduled = ScheduledOrder.objects.create(
                recurring_order=recurring,
                scheduled_date=next_order_date
            )

            for item in cart_items:
                ScheduledOrderItem.objects.create(
                    scheduled_order=scheduled,
                    product=item.product,
                    quantity=item.quantity
                )


        # CLEAR CART

        cart.items.all().delete()

        messages.success(request, "Order placed successfully!")
        return redirect("/")

    return render(request, "marketplace/checkout.html", {
        "cart": cart
    })

@login_required
def recurring_orders(request):
    scheduled_orders = ScheduledOrder.objects.filter(
        recurring_order__customer=request.user
    ).prefetch_related("items__product")

    return render(request, "marketplace/recurring_orders.html", {
        "scheduled_orders": scheduled_orders
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

    customer_profile = CustomerProfile.objects.get(user=request.user)

    orders = Order.objects.filter(customer=customer_profile).prefetch_related(
        'suborders__items__product'
    ).order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'marketplace/order_history.html', context)

@login_required
def producer_products(request):

    if not hasattr(request.user, "producerprofile"):
        return redirect("/")

    products = Product.objects.filter(producer=request.user)

    return render(request, "marketplace/producer_products.html", {
        "products": products
    })

@login_required
def edit_product(request, product_id):

    product = get_object_or_404(Product, id=product_id, producer=request.user)

    if request.method == "POST":

        product.quantity = request.POST.get("quantity")
        product.status = request.POST.get("status")
        product.season_start_month = request.POST.get("season_start_month", "").strip()
        product.season_end_month = request.POST.get("season_end_month", "").strip()

        if product.status == "all_year":
            product.season_start_month = ""
            product.season_end_month = ""

        product.save()

        messages.success(request, "Product updated successfully")

        return redirect("producer_products")

    return render(request, "marketplace/edit_product.html", {
        "product": product
    })

@login_required
def write_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Must be a customer
    if not hasattr(request.user, "customerprofile"):
        return redirect("/")

    customer = request.user.customerprofile

    # ❌ Prevent duplicate reviews
    if Review.objects.filter(product=product, customer=customer).exists():
        messages.error(request, "You have already reviewed this product.")
        return redirect("product_detail", product_id=product.id)

    # ❌ Only allow if purchased (basic check)
    if not OrderItem.objects.filter(
        product=product,
        suborder__order__customer=customer
    ).exists():
        messages.error(request, "You can only review products you have purchased.")
        return redirect("product_detail", product_id=product.id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        title = request.POST.get("title")
        text = request.POST.get("text")

        Review.objects.create(
            product=product,
            customer=customer,
            rating=rating,
            title=title,
            text=text
        )

        messages.success(request, "Review submitted!")
        return redirect("product_detail", product_id=product.id)

    return render(request, "marketplace/write_review.html", {
        "product": product
    })

def reorder(request, order_id):
    if not hasattr(request.user, "customerprofile"):
        return redirect("/")

    order = get_object_or_404(
        Order.objects.prefetch_related("suborders__items__product"),
        id=order_id,
        customer=request.user.customerprofile
    )

    cart = _get_customer_cart(request.user)

    for suborder in order.suborders.all():
        for item in suborder.items.all():
            product = item.product

            if product.quantity <= 0:
                continue

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product
            )

            if created:
                cart_item.quantity = item.quantity
            else:
                cart_item.quantity += item.quantity

            cart_item.save()

    messages.success(request, "Previous order added to cart.")
    return redirect("view_cart")

@login_required
def update_suborder_status(request, suborder_id):
    suborder = get_object_or_404(SubOrder, id=suborder_id)

    # Ensure only the producer can update it
    if suborder.producer != request.user:
        return redirect('producer_orders')

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(SubOrder.STATUS_CHOICES):
            suborder.status = new_status
            suborder.save()

    return redirect('producer_orders')

from accounts.models import Notification

@login_required
def mark_ready(request, suborder_id):
    suborder = get_object_or_404(SubOrder, id=suborder_id)

    if suborder.producer != request.user:
        return redirect('producer_orders')

    if request.method == "POST":
        if suborder.status == "pending":
            suborder.status = "ready"
            suborder.save()

            # 🔔 CREATE NOTIFICATION
            Notification.objects.create(
                customer=suborder.order.customer,
                message=f"Your order #{suborder.order.id} is ready for delivery!"
            )

    return redirect('producer_orders')

@login_required
def mark_delivered(request, suborder_id):
    suborder = get_object_or_404(SubOrder, id=suborder_id)

    if suborder.producer != request.user:
        return redirect('producer_orders')

    if request.method == "POST":
        if suborder.status == "ready":
            suborder.status = "delivered"
            suborder.save()

    return redirect('producer_orders')

def edit_scheduled_order(request, order_id):
    order = get_object_or_404(
        ScheduledOrder,
        id=order_id,
        recurring_order__customer=request.user
    )

    if request.method == "POST":

       
        if request.POST.get("delete_item"):
            item_id = request.POST.get("delete_item")
            item = get_object_or_404(
                ScheduledOrderItem,
                id=item_id,
                scheduled_order=order
            )
            item.delete()
            return redirect("edit_scheduled_order", order_id=order.id)

        
        if request.POST.get("add_product"):
            product_id = request.POST.get("new_product")
            quantity = request.POST.get("new_quantity")

            if product_id and quantity:
                product = get_object_or_404(Product, id=product_id)

                item, created = ScheduledOrderItem.objects.get_or_create(
                    scheduled_order=order,
                    product=product
                )

                if not created:
                    # already exists → increase quantity
                    item.quantity += int(quantity)
                else:
                    # new item
                    item.quantity = int(quantity)

                item.save()

            return redirect("edit_scheduled_order", order_id=order.id)

        
        if request.POST.get("save_changes"):
            for item in order.items.all():
                new_qty = request.POST.get(f"quantity_{item.id}")
                if new_qty:
                    item.quantity = int(new_qty)
                    item.save()

            return redirect("recurring_orders")

    # GET REQUEST
    return render(request, "marketplace/edit_scheduled_order.html", {
        "order": order,
        "all_products": Product.objects.all()
    })


@login_required
def cancel_suborder(request, suborder_id):
    suborder = get_object_or_404(SubOrder, id=suborder_id)

    # Ensure the current user owns the order
    if suborder.order.customer.user != request.user:
        return redirect('order_history')  # or your customer orders page

    if request.method == "POST":
        if suborder.status == "pending":
            suborder.status = "cancelled"
            suborder.save()

            # optional: notify producer
            Notification.objects.create(
                customer=suborder.order.customer,
                message=f"You cancelled Order #{suborder.order.id}."
            )

    return redirect('order_history')
