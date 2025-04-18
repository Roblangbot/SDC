from django.shortcuts import render, redirect
from .models import (ProductTable, BeigeTable, RedTable, BlueTable, GrayTable, BrownTable, YellowTable, WhiteTable, OrangeTable, PriceTable)
from .forms import ProductForm

# Create your views here.

def adminRegistration(request):
    return render(request, 'staffregister.html')

def adminLogin(request):
    return render(request, 'stafflogin.html')

def home(request):
    return render(request, 'index.html')

def aboutus(request):
    return render(request, 'about.html')

def product(request):
    # Fetch all products
    products = ProductTable.objects.all()
    
    product_data = []
    
    for product in products:
        products = ProductTable.objects.all()
        design_price = PriceTable.objects.filter(priceid=1).first()

        product_data = []
        for product in products:
            product_data.append({
                'productname': product.productname,
                'productimage': product.productimage,
                'price': design_price.amount if design_price else 0,
            })

    return render(request, 'product.html', {'products': product_data})

def itemPage(request):
    return render(request, 'itemPage.html')

def contacts(request):
    return render(request, 'contacts.html')

def cart(request):
    return render(request, 'cart.html')

def orderedItems(request):
    return render(request, 'orderItems.html')

def paymentAss(request):
    return render(request, 'paymentAss.html')

def salesMonitor(request):
    return render(request, 'salesMonitor.html')

def inventory(request):
    return render(request, 'inventory.html')

def itemCreation(request):
    # Load all color variant options
    beige_variants = BeigeTable.objects.order_by('-beigeid').values('name', 'beigeid')
    yellow_variants = YellowTable.objects.order_by('-yellowid').values('name', 'yellowid')
    red_variants = RedTable.objects.order_by('-redid').values('name', 'redid')
    white_variants = WhiteTable.objects.order_by('-whiteid').values('name', 'whiteid')
    brown_variants = BrownTable.objects.order_by('-brownid').values('name', 'brownid')
    blue_variants = BlueTable.objects.order_by('-blueid').values('name', 'blueid')
    gray_variants = GrayTable.objects.order_by('-grayid').values('name', 'grayid')
    orange_varaints = OrangeTable.objects.order_by('-orangeid').values('name', 'orangeid')
    # Add more colors here...

    if request.method == 'POST' and form.is_valid():
        form = ProductForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('itemCreation')  # or any success URL
    else:
        form = ProductForm()

    return render(request, 'itemCreation.html', {
        'form': form,
        'beige_variants': beige_variants,
        'yellow_variants': yellow_variants,
        'red_variants': red_variants,
        'white_variants': white_variants,
        'brown_variants': brown_variants,
        'blue_variants': blue_variants,
        'gray_variants': gray_variants,
        'orange_variants': orange_varaints,
        # Add more to context as needed
    })
