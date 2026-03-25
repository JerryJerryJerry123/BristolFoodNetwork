from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .forms import ProducerRegistrationForm, CustomerRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

def register(request):
    if request.method == "POST":
        user_type = request.POST.get("user_type")
        #filter register page based on user type
        if user_type == "producer":
            return redirect("register_producer")
        elif user_type == "customer":
            return redirect("register_customer")

    return render(request, "accounts/register_choice.html")

def register_producer(request):
    if request.method == 'POST':
        form = ProducerRegistrationForm(request.POST)

        if form.is_valid():
            password=form.cleaned_data['password']

            # Validate password
            try:
                validate_password(password)
            except ValidationError as e:
                form.add_error('password', e)
                return render(request, 'accounts/register.html', {
                    'form': form,
                    'user_type': 'producer'
                })
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=password
            )

            profile = form.save(commit=False)
            profile.user = user
            profile.save()

            return redirect('login')
    else:
        form = ProducerRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'user_type': 'producer'
    })


def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']

            # Validate password
            try:
                validate_password(password)
            except ValidationError as e:
                form.add_error('password', e)
                return render(request, 'accounts/register.html', {
                    'form': form,
                    'user_type': 'customer'
                })

            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=password
            )

            profile = form.save(commit=False)
            profile.user = user
            profile.save()

            return redirect('login')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'user_type': 'customer'
    })

from marketplace.models import Product
from django.utils import timezone
from datetime import timedelta
from marketplace.models import SubOrder, OrderItem, Order
from django.db.models import Sum, F
from decimal import Decimal

# Must be logged in to see settlement payments
@login_required
def producer_weekly_settlement_payments(request):

    producer = request.user

    # Ensure user is a producer
    if not hasattr(producer, 'producerprofile'):
        return redirect('/')

    # Date range: start of week till today
    today = timezone.now()

    last_april = today.replace(month=4, day=1)

    if today < last_april:
        last_april = last_april.replace(year=last_april.year - 1)

    last_monday = today - timedelta(days=today.weekday())

    print(last_april)
    print(last_monday)
    # Get suborders belonging to this producer
    weekly_suborders = SubOrder.objects.filter(
        producer=producer,
        order__created_at__range=[last_monday, today]
    )

    items_data = []
    weekly_total = Decimal("0.00")

    for suborder in weekly_suborders:
        for item in suborder.items.all():

            line_total = item.line_total
            commission = line_total * Decimal("0.05")
            producer_amount = line_total * Decimal("0.95")

            weekly_total += line_total

            items_data.append({
                "suborder_id": suborder.id,
                "date": suborder.delivery_date,
                "product": item.product.name,
                "quantity": item.quantity,
                "price": item.product.price,
                "line_total": line_total,
                "commission": commission,
                "producer_amount": producer_amount
            })

    # Get suborders for the year
    tax_year_total = Decimal("0.00")

    tax_year_suborders = SubOrder.objects.filter(
        producer=producer,
        order__created_at__range=[last_april, today]
    )

    for suborder in tax_year_suborders:
        for item in suborder.items.all():

            line_total = item.line_total
            print(line_total)
            print("line_total")
            tax_year_total += line_total

    commission_total = weekly_total * Decimal("0.05")
    producer_payment = weekly_total * Decimal("0.95")

    return render(request, "accounts/producer_weekly_settlement_payments.html", {
        "producer": producer,
        "items_data": items_data,
        "weekly_total": weekly_total,
        "tax_year_total": tax_year_total,
        "commission_total": commission_total,
        "producer_payment": producer_payment
    })

@login_required
def payments(request):
    # If user is not a producer go back to homepage
    # Get Producer Username
    producer = request.user
    if not hasattr(producer, 'producerprofile'):
        return redirect('/')
    
    return render(request, "accounts/payments.html")

@login_required
def notifications_view(request):
    notifications = request.user.customerprofile.notifications.order_by('-created_at')

    return render(request, "accounts/notifications.html", {
        "notifications": notifications
    })