from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProductForm

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