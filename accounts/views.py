from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .forms import ProducerRegistrationForm, CustomerRegistrationForm

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
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
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
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
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