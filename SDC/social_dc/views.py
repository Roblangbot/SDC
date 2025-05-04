from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import (ProductTable, BeigeTable, RedTable, BlueTable, GrayTable, BrownTable, YellowTable, WhiteTable, OrangeTable, PriceTable, SizeTable, ColorTable, OrderTable, SalesTable)
from .forms import ProductForm, variantForm
from django.utils import timezone
from django.http import HttpResponseBadRequest, HttpResponseNotFound

# Create your views here.

def adminRegistration(request):
    return render(request, 'staffregister.html')

def adminLogin(request):
    return render(request, 'stafflogin.html')

def home(request):
    return render(request, 'index.html')

def faq(request):
    return render(request, 'faq.html')

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

    # Initialize the list of color variants
    color_variants = []

    # Adding the 'Black' color variant
    black_color = ColorTable.objects.filter(colorName__iexact="Black").first()
    if black_color:
        color_variants.append({
            'name': 'Black',
            'image_url': product.productimage,
            'id': black_color.colorid  # Color ID for Black from ColorTable
        })

    # Add other colors (Blue, Beige, Red, etc.) based on their IDs and images
    if product.blueid:
        color_variants.append({
            'name': 'Blue',
            'image_url': product.blueid.blueimage,
            'id': product.blueid.colorid  # Ensure that blueid has colorid field
        })
    if product.beigeid:
        color_variants.append({
            'name': 'Beige',
            'image_url': product.beigeid.beigeimage,
            'id': product.beigeid.colorid  # Ensure that beigeid has colorid field
        })
    if product.redid:
        color_variants.append({
            'name': 'Red',
            'image_url': product.redid.redimage,
            'id': product.redid.colorid  # Ensure that redid has colorid field
        })
    if product.grayid:
        color_variants.append({
            'name': 'Gray',
            'image_url': product.grayid.grayimage,
            'id': product.grayid.colorid  # Ensure that grayid has colorid field
        })
    if product.whiteid:
        color_variants.append({
            'name': 'White',
            'image_url': product.whiteid.whiteimage,
            'id': product.whiteid.colorid  # Ensure that whiteid has colorid field
        })
    if product.brownid:
        color_variants.append({
            'name': 'Brown',
            'image_url': product.brownid.brownimage,
            'id': product.brownid.colorid  # Ensure that brownid has colorid field
        })
    if product.orangeid:
        color_variants.append({
            'name': 'Orange',
            'image_url': product.orangeid.orangeimage,
            'id': product.orangeid.colorid  # Ensure that orangeid has colorid field
        })
    if product.yellowid:
        color_variants.append({
            'name': 'Yellow',
            'image_url': product.yellowid.yellowimage,
            'id': product.yellowid.colorid  # Ensure that yellowid has colorid field
        })

    return render(request, 'productPage.html', {
        'product': product,
        'price': price,
        'color_variants': color_variants,
        'size_variants': size_variants, 
    })

def add_to_cart(request, productID):
    if request.method == 'POST':
        # Get the size, color, and quantity from the form data
        size_id = request.POST.get('sizeID')
        color_id = request.POST.get('colorID')
        quantity = request.POST.get('quantity')

        # Ensure all required data is provided
        if not size_id or not color_id or not quantity:
            return HttpResponseBadRequest("Missing required data.")

        # Retrieve the product from the database
        try:
            product = ProductTable.objects.get(productid=productID)
        except ProductTable.DoesNotExist:
            return HttpResponseNotFound("Product not found.")

        # Retrieve size and color from their respective tables
        try:
            size = SizeTable.objects.get(sizeid=size_id)
        except SizeTable.DoesNotExist:
            return HttpResponseNotFound("Size not found.")
        
        try:
            color = ColorTable.objects.get(colorid=color_id)
        except ColorTable.DoesNotExist:
            return HttpResponseNotFound("Color not found.")
        
        # Retrieve the price from PriceTable
        price = PriceTable.objects.filter(priceid=1).first()  # You can adjust the priceID as needed
        if price:
            price_amount = price.amount
        else:
            return HttpResponseNotFound("Price not found.")

        # Prepare the cart item to store in the session
        cart_item = {
            'product_id': product.productid,
            'product_name': product.productname,  # Assuming product_name is a field in ProductTable
            'size': size.size,  # Assuming size_name is a field in SizeTable
            'color': color.colorName,  # Assuming color_name is a field in ColorTable
            'quantity': quantity,
            'price': price_amount  # Assuming price is a field in ProductTable or you can use the dynamic price logic
        }

        # Retrieve the current cart from the session or initialize an empty one
        cart = request.session.get('cart', [])

        # Check if the item is already in the cart, if so, update quantity
        item_exists = False
        for item in cart:
            if item['product_id'] == cart_item['product_id'] and item['size'] == cart_item['size'] and item['color'] == cart_item['color']:
                item['quantity'] = str(int(item['quantity']) + int(cart_item['quantity']))
                item_exists = True
                break

        # If the item doesn't exist in the cart, add it
        if not item_exists:
            cart.append(cart_item)

        # Save the updated cart to the session
        request.session['cart'] = cart
        request.session.save()

        return redirect('cart')  # Redirect to cart page after adding the item

    return HttpResponseBadRequest("Invalid method.")


def remove_from_cart(request, product_id, size, color):
    # Retrieve the cart from the session
    cart = request.session.get('cart', [])

    # Filter out the item to be removed based on product_id, size, and color
    cart = [item for item in cart if not (item['product_id'] == int(product_id) and item['size'] == size and item['color'] == color)]

    # Update the session with the new cart
    request.session['cart'] = cart
    request.session.save()

    # Redirect back to the cart page
    return redirect('cart')  # Replace 'cart' with the actual name of your cart page

def cart(request):
    cart_items = request.session.get('cart', [])
    print("Cart items in session:", cart_items)  # Debugging
    
    if not cart_items:
        print("Cart is empty or data not found in session.")  # Debugging
    
    return render(request, 'cart_debug.html', {'cart_items': cart_items})

def contacts(request):
    return render(request, 'contacts.html')

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


    