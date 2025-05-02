from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import (ProductTable, BeigeTable, RedTable, BlueTable, GrayTable, BrownTable, YellowTable, WhiteTable, OrangeTable, PriceTable, SizeTable, ColorTable, OrderTable, SalesTable)
from .forms import ProductForm, variantForm
from django.utils import timezone

# Create your views here.

def adminRegistration(request):
    return render(request, 'staffregister.html')

def adminLogin(request):
    return render(request, 'stafflogin.html')

def home(request):
    return render(request, 'index.html')

def aboutus(request):
    return render(request, 'about.html')

def productCreation(request):
    # Load all color variant options
    beige_variants = BeigeTable.objects.order_by('-beigeid')  # no `.values()`
    yellow_variants = YellowTable.objects.order_by('-yellowid')
    red_variants = RedTable.objects.order_by('-redid')
    white_variants = WhiteTable.objects.order_by('-whiteid')
    brown_variants = BrownTable.objects.order_by('-brownid')
    blue_variants = BlueTable.objects.order_by('-blueid')
    gray_variants = GrayTable.objects.order_by('-grayid')
    orange_variants = OrangeTable.objects.order_by('-orangeid')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productCreation')  # Or another success page
    else:
        form = ProductForm()

    return render(request, 'productCreation.html', {
        'form': form,
        'beige_variants': beige_variants,
        'yellow_variants': yellow_variants,
        'red_variants': red_variants,
        'white_variants': white_variants,
        'brown_variants': brown_variants,
        'blue_variants': blue_variants,
        'gray_variants': gray_variants,
        'orange_variants': orange_variants,  # fixed typo
    })


def product(request):
    # Fetch all products
    products = ProductTable.objects.all()
    
    # Fetch the price once, assuming it's the same for all products
    design_price = PriceTable.objects.filter(priceid=1).first()
    price = design_price.amount if design_price else 0

    product_data = []
    for product in products:
        product_data.append({
            'id': product.productid,
            'productname': product.productname,
            'productimage': product.productimage,
            'price': price,
        })

    return render(request, 'product.html', {'products': product_data})

def productPage(request, productID):
    product = get_object_or_404(ProductTable, productid=productID)
    amount = PriceTable.objects.filter(priceid=1).first()
    price = amount.amount if amount else 0
    size_variants = SizeTable.objects.all()

    # Collect only existing color variants
    color_variants = []
    if product.blueid:
        color_variants.append({'name': 'Blue', 'image_url': product.blueid.blueimage}) 
    if product.beigeid:
        color_variants.append({'name': 'Beige', 'image_url': product.beigeid.beigeimage})
    if product.redid:
        color_variants.append({'name': 'Red', 'image_url': product.redid.redimage})
    if product.grayid:
        color_variants.append({'name': 'Gray', 'image_url': product.grayid.grayimage})
    if product.whiteid:
        color_variants.append({'name': 'White', 'image_url': product.whiteid.whiteimage})
    if product.brownid:
        color_variants.append({'name': 'Brown', 'image_url': product.brownid.brownimage})
    if product.orangeid:
        color_variants.append({'name': 'Orange', 'image_url': product.orangeid.orangeimage})
    if product.yellowid:
        color_variants.append({'name': 'Yellow', 'image_url': product.yellowid.yellowimage})

    return render(request, 'productPage.html', {
        'product': product,
        'price': price,
        'color_variants': color_variants,
        'size_variants': size_variants, 
    })

def add_to_cart(request, productID):
    if request.method == 'POST':
        size_id = request.POST.get('size_id')
        color_name = request.POST.get('color')  # Get the selected color name
        quantity = int(request.POST.get('quantity', 1))

        # Fetch product and size
        product = get_object_or_404(ProductTable, productid=productID)
        size = get_object_or_404(SizeTable, sizeid=size_id)

        # Fetch the correct color variant table based on the color selected
        if color_name == 'Beige':
            color_variant = get_object_or_404(BeigeTable)
        elif color_name == 'Blue':
            color_variant = get_object_or_404(BlueTable)
        elif color_name == 'Brown':
            color_variant = get_object_or_404(BrownTable)
        elif color_name == 'Gray':
            color_variant = get_object_or_404(GrayTable)
        elif color_name == 'Orange':
            color_variant = get_object_or_404(OrangeTable)
        elif color_name == 'Red':
            color_variant = get_object_or_404(RedTable)
        elif color_name == 'White':
            color_variant = get_object_or_404(WhiteTable)
        elif color_name == 'Yellow':
            color_variant = get_object_or_404(YellowTable)
        # Add more conditions for other color variants (e.g., Gray, White, etc.)

        # Create sales reference
        sales = SalesTable.objects.create(saledate=timezone.now())

        # Create order entry
        order = OrderTable.objects.create(
            productid=product,
            sizeid=size,
            colorid=color_variant,  # Reference to the color variant image from the selected table
            quantity=quantity,
            salesid=sales
        )

        return redirect('cart_page')  # or your desired destination
    else:
        return redirect('productPage', productID=productID)


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

def analysis(request):
    return render(request, 'analysis.html')


def variantCreation(request):
    if request.method == 'POST':
        form = variantForm(request.POST)
        if form.is_valid():
            # Check if a color image is provided and save to respective color variant tables
            if form.cleaned_data.get('beige_image'):
                beige_item = GrayTable(name=form.cleaned_data.get('name'), beigeimage=form.cleaned_data.get('beige_image'))
                beige_item.save()

            if form.cleaned_data.get('gray_image'):
                gray_item = GrayTable(name=form.cleaned_data.get('name'), grayimage=form.cleaned_data.get('gray_image'))
                gray_item.save()
            
            if form.cleaned_data.get('blue_image'):
                blue_item = BlueTable(name=form.cleaned_data.get('name'), blueimage=form.cleaned_data.get('blue_image'))
                blue_item.save()
            
            if form.cleaned_data.get('red_image'):
                red_item = RedTable(name=form.cleaned_data.get('name'), redimage=form.cleaned_data.get('red_image'))
                red_item.save()
            
            if form.cleaned_data.get('brown_image'):
                brown_item = BrownTable(name=form.cleaned_data.get('name'), brownimage=form.cleaned_data.get('brown_image'))
                brown_item.save()
            
            if form.cleaned_data.get('white_image'):
                white_item = WhiteTable(name=form.cleaned_data.get('name'), whiteimage=form.cleaned_data.get('white_image'))
                white_item.save()
            
            if form.cleaned_data.get('yellow_image'):
                yellow_item = YellowTable(name=form.cleaned_data.get('name'), yellowimage=form.cleaned_data.get('yellow_image'))
                yellow_item.save()
            
            if form.cleaned_data.get('orange_image'):
                orange_item = OrangeTable(name=form.cleaned_data.get('name'), orangeimage=form.cleaned_data.get('orange_image'))
                orange_item.save()

            # Success message
            messages.success(request, "Variant created successfully!")
    else:
        form = variantForm()  # Empty form when GET request

    return render(request, 'variantCreation.html', {'form': form})


    