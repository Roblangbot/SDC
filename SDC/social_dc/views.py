import numpy as np
import statistics
from datetime import date
from sklearn.linear_model import LinearRegression
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseNotFound, JsonResponse, HttpResponseRedirect
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from .models import (ProductTable, PriceTable, SizeTable, ColorTable, OrderTable, SalesTable, ProdNameTable)
from .forms import ProductForm
from .utils import enrich_cart
from django.core.paginator import Paginator



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
        return redirect('adminDashboard')  # Change to your desired URL or view
    return render(request, 'staffregister.html')

def adminLogin(request):
    if request.method == 'POST':
        username = request.POST['username']  # Get username from form
        password = request.POST['password']  # Get password from form
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:  # Check if user exists and is staff
            login(request, user)  # Log the user in
            return redirect('adminDashboard')  # Redirect to product creation page
        else:
            messages.error(request, 'Invalid credentials or not authorized.')  # Error message if authentication fails
    
    return render(request, 'staffLogin.html')  # Render the login template


def admin_logout(request):
    logout(request)
    return redirect('adminLogin')
# Create your views here.

def home(request):
    cart_items, total_price = enrich_cart(request.session)

    return render(request, 'index.html', {'cart_items': cart_items, 'total_price': total_price})

def faq(request):
    cart_items, total_price = enrich_cart(request.session)

    return render(request, 'faq.html', {'cart_items': cart_items, 'total_price': total_price})

def aboutus(request):
    cart_items, total_price = enrich_cart(request.session)

    return render(request, 'about.html', {'cart_items': cart_items, 'total_price': total_price})

def contacts(request):
    cart_items, total_price = enrich_cart(request.session)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = 'New Contact Form Submission'
        body = f"From: {email}\n\nMessage:\n{message}"

        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, ['yourdestination@example.com'])
            messages.success(request, "Your message has been sent successfully!")
        except:
            messages.error(request, "Something went wrong. Please try again.")

        return redirect('contact')  # or redirect to a thank-you page

    return render(request, 'contacts.html', {'cart_items': cart_items, 'total_price': total_price})

def checkout(request):
    cart_items = request.session.get('cart', [])
    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect('product')

    total_price = 0
    for item in cart_items:
        item['subtotal'] = int(item['price']) * int(item['quantity'])
        total_price += item['subtotal']

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def product(request):
    # --- FILTER HANDLING ---
    filter_type = request.GET.get("filter")  # e.g., ?filter=best_seller

    # Always fetch the black color (used as display image)
    black_color = ColorTable.objects.filter(colorname__iexact="Black").first()

    # Count the total number of colors available
    total_colors = ColorTable.objects.count()

    if not black_color:
        products = ProductTable.objects.none()
    else:
        # Default query: only show black variant
        products = ProductTable.objects.filter(colorid=black_color).select_related("prodnameid", "colorid")

        # Apply filters dynamically
        if filter_type == "best_seller":
            products = products.annotate(order_count=Count("ordertable")).order_by("-order_count")[:10]

        elif filter_type == "complete_color":
            # Products that have all color variants
            products = products.annotate(
                color_variants=Count("prodnameid__producttable", distinct=True)
            ).filter(color_variants=total_colors)

        elif filter_type == "limited_color":
            # Products that have fewer color variants than total available
            products = products.annotate(
                color_variants=Count("prodnameid__producttable", distinct=True)
            ).filter(color_variants__lt=total_colors)

    # --- CART + PRICE ---
    cart_items, total_price = enrich_cart(request.session)

    design_price = PriceTable.objects.filter(priceid=1).first()
    price = design_price.amount if design_price else 0

    # --- PRODUCT DATA ---
    product_data = []
    for product in products:
        product_data.append({
            "id": product.productid,
            "productname": product.prodnameid.name if product.prodnameid else "Unnamed",
            "productimage": product.productimage,
            "price": price,
        })

    # --- PAGINATION ---
    paginator = Paginator(product_data, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "product.html", {
        "page_obj": page_obj,
        "cart_items": cart_items,
        "total_price": total_price
    })

def productPage(request, productID):
 # Main product (with joins for prodname and color)
    product = get_object_or_404(
        ProductTable.objects.select_related("prodnameid", "colorid"),
        productid=productID
    )

    # Get Black color object
    black_color = ColorTable.objects.filter(colorname__iexact="Black").first()

    # Default variant: Prefer Black if it exists, otherwise the current product
    default_variant = ProductTable.objects.filter(
        prodnameid=product.prodnameid,
        colorid=black_color
    ).first() or product

    # Fetch all other color variants (excluding Black)
    colors = ProductTable.objects.filter(
        prodnameid=product.prodnameid
    )

    # ✅ Define color_variants_data
    color_variants_data = []
    for variant in colors:
        color_variants_data.append({
            "id": variant.productid,    
            "color": variant.colorid.colorname if variant.colorid else "Unknown",
            "image": variant.productimage,
        })

    # Price
    price = default_variant.priceid.amount if default_variant.priceid else 0

    # Sizes + cart
    size_variants = SizeTable.objects.all()
    cart_items, total_price = enrich_cart(request.session)

    # ✅ Pass it to template
    return render(request, 'productPage.html', {
        "product": default_variant,
        "color_variants_data": color_variants_data,
        "price": price,
        "size_variants": size_variants,
        "cart_items": cart_items,
        "total_price": total_price,
    })

def add_to_cart(request):
    if request.method == 'POST':
        size_id = request.POST.get('sizeID')
        quantity = request.POST.get('quantity')
        product_id = request.POST.get('productID')

        if not product_id:
            return HttpResponseBadRequest("Product ID is missing.")
        if not size_id or not quantity:
            return HttpResponseBadRequest("Missing required data.")

        try:
            product = ProductTable.objects.select_related('colorid', 'prodnameid', 'priceid').get(productid=product_id)
        except ProductTable.DoesNotExist:
            return HttpResponseBadRequest("Product does not exist.")
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        try:
            size = SizeTable.objects.get(sizeid=size_id)
        except SizeTable.DoesNotExist:
            return HttpResponseBadRequest("Size does not exist.")

        # If no errors, continue processing...
        cart_item = {
            'product_id': product.productid,
            'product_name': product.prodnameid.name,
            'size': size.size,
            'color': product.colorid.colorname,
            'quantity': quantity,
            'price': product.priceid.amount,
            'image_url': product.productimage,
        }

        cart = request.session.get('cart', [])

        # Merge if duplicate
        for item in cart:
            if item['product_id'] == cart_item['product_id'] and item['size'] == cart_item['size']:
                item['quantity'] = str(int(item['quantity']) + int(quantity))
                break
        else:
            cart.append(cart_item)

        request.session['cart'] = cart
        request.session.modified = True

        return redirect('productPage', productID=product.productid)

    return HttpResponseBadRequest("Invalid method.")


def remove_from_cart(request, product_id, size):
    cart = request.session.get("cart", [])
    cart = [item for item in cart if not (item["product_id"] == product_id and item["size"] == size)]

    request.session["cart"] = cart
    request.session.modified = True

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)


def update_cart_quantity(request, product_id, size):
    if request.method == "POST":
        new_qty = int(request.POST.get("quantity", 1))
        cart = request.session.get("cart", [])

        for item in cart:
            if item["product_id"] == product_id and item["size"] == size:
                item["quantity"] = new_qty
                item["subtotal"] = item["quantity"] * item["price"]
                break

        request.session["cart"] = cart
        request.session.modified = True

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)

def cart(request):
    cart_items = request.session.get("cart", [])

    # Calculate subtotal per item & total
    total_price = 0
    for item in cart_items:
        item["subtotal"] = int(item["price"]) * int(item["quantity"])
        total_price += item["subtotal"]

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total_price": total_price,
    })


@login_required(login_url='adminLogin')
def adminDashboard(request):
    return render(request, 'adminDashboard.html')

@login_required(login_url='adminLogin')
def addProduct(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST)

        if product_form.is_valid():
            product_form.save()
            return redirect('addProduct')
    else:
        product_form = ProductForm()

    products = ProductTable.objects.all()

    context = {
        'products' : products,
        'product_form': product_form
    }

    return render(request, 'addProduct.html', context)

@login_required(login_url='adminLogin')
def orderedItems(request):
    # Fetch all orders with related tables (e.g., size, product, color)
    orders = OrderTable.objects.all().order_by('orderid')  # Ascendin

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


    return render(request, 'variantCreation.html')

# DATA ANALYSIS
@login_required(login_url='adminLogin')
def salesMonitor(request):
    # # Filter April to May 2023
    # start_date = date(2023, 4, 1)
    # end_date = date(2023, 5, 31)

    # # Filter order records through sales date
    # orders_apr_may = OrderTable.objects.filter(salesid__sales_date__range=(start_date, end_date))
    # sales_apr_may = SalesTable.objects.filter(sales_date__range=(start_date, end_date))

    # # Most Bought Color
    # color_data = orders_apr_may.values('colorid__colorName') \
    #     .annotate(total=Sum('quantity')).order_by('-total')

    # # Most Bought Design (Product)
    # design_data = orders_apr_may.values('productid__productname') \
    #     .annotate(total=Sum('quantity')).order_by('-total')

    # # Most Bought Size
    # size_data = orders_apr_may.values('sizeid__size') \
    #     .annotate(total=Sum('quantity')).order_by('-total')

    # # Most Bought Product + Color Combo
    # combo_data = orders_apr_may.values('productid__productname', 'colorid__colorName') \
    #     .annotate(total=Sum('quantity')).order_by('-total')

    # # Get daily or monthly sales based on the request
    # sales_timeframe = request.GET.get('timeframe', 'month')  # Default to 'month'

    # if sales_timeframe == 'day':
    #     # Group by day if 'day' is selected
    #     sales_data = sales_apr_may.annotate(day=TruncDay('sales_date')) \
    #         .values('day').annotate(total=Count('salesid')).order_by('day')
    #     timeframe_labels = [s['day'].strftime('%d %b') for s in sales_data]  # Display as "Day Month"
    # else:
    #     # Group by month if 'month' is selected
    #     sales_data = sales_apr_may.annotate(month=TruncMonth('sales_date')) \
    #         .values('month').annotate(total=Count('salesid')).order_by('month')
    #     timeframe_labels = [s['month'].strftime('%b').upper() for s in sales_data]  # Display as "Month"

    # # Context for displaying sales data
    # context = {
    #     'color_labels': [c['colorid__colorName'] for c in color_data],
    #     'color_totals': [c['total'] for c in color_data],

    #     'design_labels': [d['productid__productname'] for d in design_data],
    #     'design_totals': [d['total'] for d in design_data],

    #     'size_labels': [s['sizeid__size'] for s in size_data],
    #     'size_totals': [s['total'] for s in size_data],

    #     'combo_labels': [f"{c['productid__productname']}/{c['colorid__colorName']}" for c in combo_data[:5]],
    #     'combo_totals': [c['total'] for c in combo_data[:5]],

    #     'sales_labels': timeframe_labels,
    #     'sales_totals': [s['total'] for s in sales_data],
    # }

    # # Convert dates to numerical values for regression
    # linearx = np.arange(len(sales_data)).reshape(-1, 1)
    # lineary = np.array([s['total'] for s in sales_data])

    # # Only run if enough data points
    # trend = None
    # if len(linearx) >= 2:
    #     model = LinearRegression().fit(linearx, lineary)
    #     slope = model.coef_[0]
    #     if slope > 0:
    #         trend = "Increasing trend"
    #     elif slope < 0:
    #         trend = "Decreasing trend"
    #     else:
    #         trend = "Stable sales"

    # # Add to context
    # context['sales_trend'] = trend

    # sales_values = [s['total'] for s in sales_data]
    # if len(sales_values) >= 2:
    #     mean = statistics.mean(sales_values)
    #     stdev = statistics.stdev(sales_values)
    #     outliers = [label for i, label in enumerate(timeframe_labels)
    #                 if abs(sales_values[i] - mean) > 2 * stdev]

    #     context['outlier_periods'] = outliers


    return render(request, 'salesMonitor.html', 
                #   context
                  )