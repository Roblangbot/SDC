import numpy as np
import statistics
from datetime import date
from sklearn.linear_model import LinearRegression
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from .models import (ProductTable, BeigeTable, RedTable, BlueTable, GrayTable, BrownTable, YellowTable, WhiteTable, OrangeTable, PriceTable, SizeTable, ColorTable, OrderTable, SalesTable)
from .forms import ProductForm, variantForm


def adminRegister(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Password match check
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('adminRegister')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('adminRegister')

        # Create the admin user
        user = User.objects.create_user(username=username, password=password1, first_name=first_name, last_name=last_name)
        user.is_staff = True  # Mark the user as an admin
        user.save()

        # Log the user in automatically after registration
        login(request, user)

        # Redirect to admin dashboard or a welcome page
        return redirect('productCreation')  # Change to your desired URL or view
    return render(request, 'staffregister.html')

def adminLogin(request):
    if request.method == 'POST':
        username = request.POST['username']  # Get username from form
        password = request.POST['password']  # Get password from form
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:  # Check if user exists and is staff
            login(request, user)  # Log the user in
            return redirect('productCreation')  # Redirect to product creation page
        else:
            messages.error(request, 'Invalid credentials or not authorized.')  # Error message if authentication fails
    
    return render(request, 'staffLogin.html')  # Render the login template


def admin_logout(request):
    logout(request)
    return redirect('staffLogin.html')
# Create your views here.

def home(request):
    return render(request, 'index.html')

def faq(request):
    return render(request, 'faq.html')

def aboutus(request):
    return render(request, 'about.html')

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

@login_required(login_url='adminLogin')
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

@login_required(login_url='adminLogin')
def orderedItems(request):
    # Fetch all orders with related tables (e.g., size, product, color)
    orders = OrderTable.objects.all().order_by('orderid')  # Ascendin

    # Debugging: log the number of orders
    print(f"Total Orders: {orders.count()}")  # This will show in your console or server log

    # Pass the orders to the template
    context = {
        'orders': orders
    }
    
    return render(request, 'orderItems.html', context)

@login_required(login_url='adminLogin')
def paymentAss(request):
    return render(request, 'paymentAss.html')

@login_required(login_url='adminLogin')
def inventory(request):
    return render(request, 'inventory.html')

@login_required(login_url='adminLogin')
def analysis(request):
    return render(request, 'analysis.html')

@login_required(login_url='adminLogin')
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

# DATA ANALYSIS
@login_required(login_url='adminLogin')
def salesMonitor(request):
    # Filter April to May 2023
    start_date = date(2023, 4, 1)
    end_date = date(2023, 5, 31)

    # Filter order records through sales date
    orders_apr_may = OrderTable.objects.filter(salesid__sales_date__range=(start_date, end_date))
    sales_apr_may = SalesTable.objects.filter(sales_date__range=(start_date, end_date))

    # Most Bought Color
    color_data = orders_apr_may.values('colorid__colorName') \
        .annotate(total=Sum('quantity')).order_by('-total')

    # Most Bought Design (Product)
    design_data = orders_apr_may.values('productid__productname') \
        .annotate(total=Sum('quantity')).order_by('-total')

    # Most Bought Size
    size_data = orders_apr_may.values('sizeid__size') \
        .annotate(total=Sum('quantity')).order_by('-total')

    # Most Bought Product + Color Combo
    combo_data = orders_apr_may.values('productid__productname', 'colorid__colorName') \
        .annotate(total=Sum('quantity')).order_by('-total')

    # Get daily or monthly sales based on the request
    sales_timeframe = request.GET.get('timeframe', 'month')  # Default to 'month'

    if sales_timeframe == 'day':
        # Group by day if 'day' is selected
        sales_data = sales_apr_may.annotate(day=TruncDay('sales_date')) \
            .values('day').annotate(total=Count('salesid')).order_by('day')
        timeframe_labels = [s['day'].strftime('%d %b') for s in sales_data]  # Display as "Day Month"
    else:
        # Group by month if 'month' is selected
        sales_data = sales_apr_may.annotate(month=TruncMonth('sales_date')) \
            .values('month').annotate(total=Count('salesid')).order_by('month')
        timeframe_labels = [s['month'].strftime('%b').upper() for s in sales_data]  # Display as "Month"

    # Context for displaying sales data
    context = {
        'color_labels': [c['colorid__colorName'] for c in color_data],
        'color_totals': [c['total'] for c in color_data],

        'design_labels': [d['productid__productname'] for d in design_data],
        'design_totals': [d['total'] for d in design_data],

        'size_labels': [s['sizeid__size'] for s in size_data],
        'size_totals': [s['total'] for s in size_data],

        'combo_labels': [f"{c['productid__productname']}/{c['colorid__colorName']}" for c in combo_data[:5]],
        'combo_totals': [c['total'] for c in combo_data[:5]],

        'sales_labels': timeframe_labels,
        'sales_totals': [s['total'] for s in sales_data],
    }

    # Convert dates to numerical values for regression
    linearx = np.arange(len(sales_data)).reshape(-1, 1)
    lineary = np.array([s['total'] for s in sales_data])

    # Only run if enough data points
    trend = None
    if len(linearx) >= 2:
        model = LinearRegression().fit(linearx, lineary)
        slope = model.coef_[0]
        if slope > 0:
            trend = "Increasing trend"
        elif slope < 0:
            trend = "Decreasing trend"
        else:
            trend = "Stable sales"

    # Add to context
    context['sales_trend'] = trend

    sales_values = [s['total'] for s in sales_data]
    if len(sales_values) >= 2:
        mean = statistics.mean(sales_values)
        stdev = statistics.stdev(sales_values)
        outliers = [label for i, label in enumerate(timeframe_labels)
                    if abs(sales_values[i] - mean) > 2 * stdev]

        context['outlier_periods'] = outliers


    return render(request, 'salesMonitor.html', context)