import numpy as np
import statistics, pytz, json, random
from datetime import date
from sklearn.linear_model import LinearRegression
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseNotFound, JsonResponse, HttpResponseRedirect
from django.db.models import Sum, Count, Avg, Q, OuterRef, Subquery, Case, When, Value, IntegerField, F, DecimalField
from django.db.models.functions import TruncMonth, TruncDay, TruncWeek, TruncYear, Coalesce
from calendar import monthrange
from django.utils.timezone import localtime, now
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import timedelta
from .models import (ProductTable, PendingOrder, PaystatTable, ProdNameTable, PriceTable, ItemStatusTable, SizeTable, ColorTable, OrderTable, SalesTable, PaymentTable, CustomerTable, SalesAddressTable, RegionTable, ProvinceTable, CityMunicipalityTable, BarangayTable)
from .forms import ProductForm, CombinedStatusForm, ProdNameForm
from .utils import enrich_cart, generate_otp, send_order_otp, cleanup_expired_otps
import statistics
from django.core.paginator import Paginator
from datetime import datetime   
from django.views import View


# Define Manila timezone
manila_tz = pytz.timezone('Asia/Manila')

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
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')  # Will be 'on' if checked

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)

            # If "Remember me" is not checked, expire session on browser close
            if not remember_me:
                request.session.set_expiry(0)  # Session expires on browser close
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days

            return redirect('adminDashboard')
        else:
            messages.error(request, 'Invalid credentials or not authorized.')

    return render(request, 'staffLogin.html')


def admin_logout(request):
    logout(request)
    return redirect('adminLogin')


def home(request):
    cart_items, total_price = enrich_cart(request.session)

    best_seller_data = (
        OrderTable.objects
        .values('productid')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:3]
    )

    best_seller_ids = [item['productid'] for item in best_seller_data]

    best_selling_products_queryset = ProductTable.objects.filter(productid__in=best_seller_ids)

    best_selling_products = sorted(
        best_selling_products_queryset,
        key=lambda product: best_seller_ids.index(product.productid)
    )
    sizes_qs = SizeTable.objects.all()
    sizes_list = list(sizes_qs.values('sizeid', 'size'))

    sizes_by_product = {product.productid: sizes_list for product in best_selling_products}

    for product in best_selling_products:
        product.sizes = sizes_by_product.get(product.productid, [])

    return render(request, 'index.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'best_selling_products': best_selling_products
    })

@require_POST
def buy_now(request):
    product_id = request.POST.get('productID')
    size_id = request.POST.get('sizeID')
    price_id = request.POST.get('priceID')
    quantity = request.POST.get('quantity', 1)

    try:
        product = ProductTable.objects.get(pk=product_id)
        size = SizeTable.objects.get(pk=size_id)
        price = PriceTable.objects.get(pk=price_id)
    except (ProductTable.DoesNotExist, SizeTable.DoesNotExist, PriceTable.DoesNotExist):
        messages.error(request, "Invalid product selection.")
        return redirect('home') 

    cart_item = {
        'product_id': product.productid,
        'product_name': product.prodnameid.name,
        'size': size.size,
        'size_id': size.sizeid,
        'color': product.colorid.colorname,
        'quantity': quantity,
        'price': price.amount,
        'price_id': price.priceid,
        'image_url': product.productimage,
    }

    request.session['cart'] = [cart_item]
    request.session.modified = True

    return redirect('checkout')

def faq(request):
    cart_items, total_price = enrich_cart(request.session)

    return render(request, 'faq.html', {'cart_items': cart_items, 'total_price': total_price})

def aboutus(request):
    cart_items, total_price = enrich_cart(request.session)

    return render(request, 'about.html', {'cart_items': cart_items, 'total_price': total_price})

def contacts(request):
    cart_items, total_price = enrich_cart(request.session)

    if request.method == 'POST':
        sender_email = request.POST.get('email')
        message = request.POST.get('message')

        subject = 'New Contact Form Submission'
        body = f"Message from: {sender_email}\n\n{message}"

        try:
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.DEFAULT_FROM_EMAIL],
                reply_to=[sender_email]
            )
            email.send()
            messages.success(request, "Your message has been sent successfully!")
        except Exception as e:
            messages.error(request, f"Something went wrong. {e}")

        return redirect('contacts')

    return render(request, 'contacts.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

def process_order(order_data):
    from django.utils.timezone import localtime, now
    from django.contrib import messages

    # Extract core data
    first_name = order_data.get('first_name')
    last_name = order_data.get('last_name')
    contact_no = order_data.get('contact_no')
    email = order_data.get('email')

    # ✅ Get the most recent customer record (safe even with duplicates)
    customer = CustomerTable.objects.filter(email=email).order_by('-customerid').first()

    # If no existing record, create a new one
    if not customer:
        customer = CustomerTable.objects.create(
            firstname=first_name,
            lastname=last_name,
            contactno=contact_no,
            email=email
        )

    # 2️⃣ Compute total
    cart_items = order_data.get('cart_items', [])
    total_price = sum(int(item['price']) * int(item['quantity']) for item in cart_items)

    # 3️⃣ Create SalesTable record
    status = ItemStatusTable.objects.get(pk=1)
    local_now = localtime(now())

    sales = SalesTable.objects.create(
        ordernumber=f"ORD-{local_now.strftime('%Y%m%d%H%M%S')}",
        customerid=customer,
        total_price=total_price,
        itemstatusid=status,
        sales_date=local_now.date(),
        sales_time=local_now.time()
    )

    # 4️⃣ Address
    SalesAddressTable.objects.create(
        salesid=sales,
        full_address=order_data.get('full_address'),
        latitude=order_data.get('latitude'),
        longitude=order_data.get('longitude'),
        delivery_instructions=order_data.get('delivery_instructions'),
        createdat=now()
    )

    # 5️⃣ Create OrderTable items
    for item in cart_items:
        try:
            product = ProductTable.objects.get(pk=item['product_id'])
            size = SizeTable.objects.get(pk=item['size_id'])
            price = PriceTable.objects.get(pk=item['price_id'])

            existing_order = OrderTable.objects.filter(
                salesid=sales,
                productid=product,
                sizeid=size
            ).first()

            if existing_order:
                existing_order.quantity += int(item['quantity'])
                existing_order.save()
            else:
                OrderTable.objects.create(
                    salesid=sales,
                    productid=product,
                    sizeid=size,
                    priceid=price,
                    quantity=int(item['quantity']),
                )

        except Exception as e:
            print(f"❌ Error saving item '{item.get('product_name')}': {e}")

    # 6️⃣ Payment info
    paystat = PaystatTable.objects.get(pk=1)
    PaymentTable.objects.create(
        salesid=sales,
        mop=order_data.get('payment_method'),
        date=now().date(),
        time=now().time(),
        paystatid=paystat,
    )

    print("✅ Order successfully created for", customer.email)
    return sales

class VerifyOrderOTPView(View):
    def post(self, request):
        cleanup_expired_otps()
        try:
            data = json.loads(request.body)
            print("DEBUG OTP DATA:", data)

            email = data.get("email")
            entered_otp = data.get("otp")

            if not email or not entered_otp:
                print("DEBUG ERROR: Missing email or OTP")
                return JsonResponse({"error": "Missing data"}, status=400)

            # ✅ Get the *most recent* customer record with this email
            customer = CustomerTable.objects.filter(email=email).last()
            if not customer:
                print("DEBUG ERROR: Customer not found for email:", email)
                return JsonResponse({"error": "Customer not found"}, status=404)

            print("DEBUG STEP: Customer found", customer.pk, customer.email)

            # ✅ Look up pending order
            try:
                pending_order = PendingOrder.objects.filter(
                    customerid=customer,
                    is_verified=False
                ).latest("created_at")
                print("DEBUG STEP: Pending order found:", pending_order.pk)

            except PendingOrder.DoesNotExist:
                print("DEBUG ERROR: No pending order for customer")
                return JsonResponse({"error": "No pending order found"}, status=404)
                
            except Exception as e:
                print("DEBUG ERROR: Pending order lookup failed:", e)
                return JsonResponse({"error": f"Pending order error: {e}"}, status=400)

            # ✅ Check OTP expiry
            if pending_order.is_expired():
                print("DEBUG ERROR: OTP expired")
                return JsonResponse({"error": "OTP expired"}, status=400)

            print("DEBUG STEP: Comparing entered OTP with stored:", entered_otp, pending_order.otp)

            if pending_order.otp != entered_otp:
                print("DEBUG ERROR: Incorrect OTP")
                return JsonResponse({"error": "Incorrect OTP"}, status=400)

            # ✅ Mark as verified
            pending_order.is_verified = True
            pending_order.save()
            print("DEBUG STEP: OTP verified successfully")

            # ✅ Process the order
            order_data = pending_order.order_data
            print("DEBUG STEP: Processing order_data:", order_data)

            sales = process_order(order_data)  # 👈 create real order records

            if 'cart' in request.session:
                request.session['cart'] = []
                request.session.modified = True
                print("✅ Cart cleared after verified OTP")
                
            # ✅ Clean up
            pending_order.delete()

            print("DEBUG STEP: Pending order deleted and order created:", sales.ordernumber)

            return JsonResponse({
                "status": "verified",
                "message": "Order confirmed successfully!"
            })

        except Exception as e:
            print("DEBUG CRITICAL ERROR:", e)
            return JsonResponse({"error": f"Server error: {e}"}, status=500)

def generate_otp():
    """Generate a 6-digit random OTP"""
    return str(random.randint(100000, 999999))

class OrderRequestView(View):
    def post(self, request):
        try:
            cleanup_expired_otps()
            data = json.loads(request.body)
            email = data.get("email")
            order_data = data.get("order_data", {})

            if not email:
                return JsonResponse({"status": "error", "message": "Email is required."}, status=400)

            # ✅ Use .filter() and take the most recent (not .get())
            customer = CustomerTable.objects.filter(email=email).order_by('-customerid').first()

            if not customer:
                # Optional: Create a new record for new buyer
                customer = CustomerTable.objects.create(
                    firstname=order_data.get("first_name", ""),
                    lastname=order_data.get("last_name", ""),
                    contactno=order_data.get("contact_no", ""),
                    email=email
                )

            # ✅ Generate a 6-digit OTP
            otp = str(random.randint(100000, 999999))

            # ✅ Send OTP (email or console)
            send_order_otp(customer.email, otp)

            # ✅ Create pending order entry (attach JSON order_data)
            PendingOrder.objects.create(
                customerid=customer,
                otp=otp,
                order_data=order_data
            )

            return JsonResponse({"status": "sent", "message": "OTP sent successfully."})

        except Exception as e:
            print("OTP sending failed:", e)
            return JsonResponse({"status": "error", "message": f"Failed to send OTP: {e}"}, status=500)

def checkout(request):
    cart_items = request.session.get('cart', [])
    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect('product')

    if request.method == "POST":
        # 1. Get customer info
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        contact_no = request.POST.get('contact_no')
        email = request.POST.get('email')

        # 2. Create customer
        customer = CustomerTable.objects.create(
            firstname=first_name,
            lastname=last_name,
            contactno=contact_no,
            email=email
        )

        total_price = sum(int(item['price']) * int(item['quantity']) for item in cart_items)
        status = ItemStatusTable.objects.get(pk=1)
        local_now = localtime(now())

        sales = SalesTable.objects.create(
            ordernumber=f"ORD-{local_now.strftime('%Y%m%d%H%M%S')}",
            customerid=customer,
            total_price=total_price,
            itemstatusid=status,
            sales_date=local_now.date(),
            sales_time=local_now.time()
        )

        SalesAddressTable.objects.create(
            salesid=sales,
            full_address=request.POST.get('full_address'),
            latitude=request.POST.get('latitude'),
            longitude=request.POST.get('longitude'),
            delivery_instructions=request.POST.get('delivery_instructions'),
            createdat=timezone.now()
        )

        for item in cart_items:
            try:
                product = ProductTable.objects.get(pk=item['product_id'])
                size = SizeTable.objects.get(pk=item['size_id'])
                price = PriceTable.objects.get(pk=item['price_id'])

                existing_order = OrderTable.objects.filter(
                    salesid=sales,
                    productid=product,
                    sizeid=size
                ).first()

                if existing_order:
                    existing_order.quantity += int(item['quantity'])
                    existing_order.save()
                else:
                    OrderTable.objects.create(
                        salesid=sales,
                        productid=product,
                        sizeid=size,
                        priceid=price,
                        quantity=int(item['quantity']),
                    )

            except Exception as e:
                print(f"❌ Error saving item '{item['product_name']}': {e}")

        paystat = PaystatTable.objects.get(pk=1)
        PaymentTable.objects.create(
            salesid=sales,
            mop=request.POST.get('payment_method'),
            date=timezone.now().date(),
            time=timezone.now().time(),
            paystatid=paystat,
        )

        request.session['cart'] = []
        return redirect('order_success')

    total_price = sum(int(item['price']) * int(item['quantity']) for item in cart_items)
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

@require_POST
def buy_now(request):
    product_id = request.POST.get('productID')
    size_id = request.POST.get('sizeID')
    price_id = request.POST.get('priceID')
    quantity = request.POST.get('quantity', 1)

    try:
        product = ProductTable.objects.get(pk=product_id)
        size = SizeTable.objects.get(pk=size_id)
        price = PriceTable.objects.get(pk=price_id)
    except (ProductTable.DoesNotExist, SizeTable.DoesNotExist, PriceTable.DoesNotExist):
        messages.error(request, "Invalid product selection.")
        return redirect('home')


    cart_item = {
        'product_id': product.productid,
        'product_name': product.prodnameid.name,
        'size': size.size,
        'size_id': size.sizeid,
        'color': product.colorid.colorname,
        'quantity': quantity,
        'price': price.amount,
        'price_id': price.priceid,
        'image_url': product.productimage,
    }

    request.session['cart'] = [cart_item]
    request.session.modified = True

    return redirect('checkout')

def order_success(request):
    return render(request, 'success.html')


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

        if filter_type == "best_seller":
            # Step 1: Aggregate total quantity sold per product (top 10)
            best_seller_data = (
                OrderTable.objects
                .values('productid')
                .annotate(total_sold=Sum('quantity'))
                .order_by('-total_sold')[:10]
            )

            # Step 2: Extract product IDs
            best_seller_ids = [item['productid'] for item in best_seller_data]

            # Step 3: Fetch full ProductTable objects matching those IDs
            products = ProductTable.objects.filter(productid__in=best_seller_ids)

            # Step 4: Sort them to match the best-selling order
            products = sorted(products, key=lambda p: best_seller_ids.index(p.productid))

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

    page_obj.object_list = list(page_obj.object_list)
    random.shuffle(page_obj.object_list)

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
        try:
            size_id = request.POST.get('sizeID')
            quantity = int(request.POST.get('quantity', 1))
            product_id = request.POST.get('productID')

            if not (size_id and product_id):
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Missing size or product ID.'})
                else:
                    messages.error(request, "Missing size or product ID.")
                    return redirect('productPage', productID=product_id)

            product = ProductTable.objects.select_related('colorid', 'prodnameid', 'priceid').get(productid=product_id)
            size = SizeTable.objects.get(sizeid=size_id)

            image_url = product.productimage.url if hasattr(product.productimage, 'url') else product.productimage

            cart_item = {
                'product_id': product.productid,
                'product_name': product.prodnameid.name,
                'size': size.size,
                'size_id': size.sizeid,
                'color': product.colorid.colorname,
                'quantity': quantity,
                'price': product.priceid.amount,
                'price_id': product.priceid.priceid,
                'image_url': image_url,
            }

            cart = request.session.get('cart', [])
            for item in cart:
                if item['product_id'] == cart_item['product_id'] and item['size'] == cart_item['size']:
                    item['quantity'] += quantity
                    if item['quantity'] >= 50:
                        item['quantity'] = 50
                    break
            else:
                cart.append(cart_item)

            request.session['cart'] = cart
            request.session.modified = True
            
            total_item_count = len(cart)
            request.session['total_item_count'] = total_item_count

            # Recalculate subtotals and total price
            total_price = 0
            for item in cart:
                item['subtotal'] = item['quantity'] * item['price']
                total_price += item['subtotal']

            # If AJAX request, return JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                cart_html = render_to_string('cart/_cart_items.html', {
                    'cart_items': cart,
                    'total_price': total_price,
                }, request=request)

                return JsonResponse({
                    'success': True,
                    'total_item_count': total_item_count,
                    'cart_html': cart_html,
                })

            # Non-AJAX fallback
            messages.success(request, "Item added to cart successfully!")
            return redirect('productPage', productID=product_id)
            
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print("POST data:", request.POST)
            print(tb)  # view console / server logs
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e), 'traceback': tb})
            else : messages.error(request, f"Something went wrong: {str(e)}")
            return redirect('productPage', productID=request.POST.get('productID'))

    return HttpResponseBadRequest("Invalid request method.")

def update_cart_quantity(request, product_id, size):
    if request.method == "POST":
        new_qty = int(request.POST.get("quantity", 1))
        cart = request.session.get("cart", [])
        total_price = 0

        for item in cart:
            if item["product_id"] == product_id and item["size"] == size:
                item["quantity"] = new_qty
                item["subtotal"] = item["quantity"] * item["price"]
            total_price += item.get("subtotal", item["quantity"] * item["price"])

        request.session["cart"] = cart
        request.session.modified = True
        request.session["total_item_count"] = len(cart)

        print(f"Updated cart: {cart}")

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            cart_html = render_to_string('cart/_cart_items.html', {
                'cart_items': cart,
                'total_price': total_price
            }, request=request)

            return JsonResponse({
                'success': True,
                'cart_html': cart_html,
                'total_item_count': request.session["total_item_count"]
            })

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def remove_from_cart(request, product_id, size):
    cart = request.session.get("cart", [])
    cart = [item for item in cart if not (item["product_id"] == product_id and item["size"] == size)]

    request.session["cart"] = cart
    request.session.modified = True
    request.session["total_item_count"] = len(cart)

    total_price = sum(item["price"] * item["quantity"] for item in cart)
    for item in cart:
        item["subtotal"] = item["quantity"] * item["price"]

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_html = render_to_string('cart/_cart_items.html', {
            'cart_items': cart,
            'total_price': total_price
        }, request=request)

        return JsonResponse({
            'success': True,
            'cart_html': cart_html,
            'total_item_count': request.session["total_item_count"]
        })

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='adminLogin')
def adminDashboard(request):
    today = date.today()
    start_date = today - timedelta(days=29)  # last 30 days including today
    end_date = today

    # Fetch orders and sales in current month
    orders = OrderTable.objects.filter(salesid__sales_date__range=(start_date, end_date))
    sales = SalesTable.objects.filter(sales_date__range=(start_date, end_date))

    # 1. Sales Over Time (Daily Aggregation)
    sales_time_data = sales.annotate(day=TruncDay('sales_date')) \
        .values('day') \
        .annotate(total_sales=Sum('total_price')) \
        .order_by('day')

    sales_labels = [item['day'].strftime('%d %b') if item['day'] else '' for item in sales_time_data]
    sales_totals = [item['total_sales'] or 0 for item in sales_time_data]

    # 2. Recent Orders (Latest 4)
    recent_orders_qs = orders.select_related(
        'productid__prodnameid',
        'productid__colorid',
        'salesid__customerid'
    ).order_by('-salesid__sales_date')[:4]

    recent_orders = []
    for o in recent_orders_qs:
        # Combine sales_date and sales_time into a datetime
        if o.salesid.sales_date and o.salesid.sales_time:
            dt_naive = datetime.combine(o.salesid.sales_date, o.salesid.sales_time)
            # Convert naive datetime to aware datetime in Manila timezone
            dt_aware = manila_tz.localize(dt_naive)
        else:
            dt_aware = None  # fallback if either field missing

        recent_orders.append({
            'order_id': o.salesid.salesid,
            'product_name': o.productid.prodnameid.name,
            'customer_name': o.salesid.customerid.firstname,
            'time_diff': dt_aware,
            'amount': o.quantity * getattr(o.productid.priceid, 'amount', 0),
            'image_url': getattr(o.productid, 'productimage', ''),  # safer access
        })

    # 3. Top-Selling Products
    top_products_data = (
        orders
        .values('productid', 'productid__prodnameid__name', 'productid__productimage', 'productid__priceid__amount')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty')[:5]
    )

    # Status badge mapping
    badge_map = {
        'Delivered': 'text-bg-success',
        'Pending': 'text-bg-warning',
        'Cancelled': 'text-bg-danger'
    }

    top_products = []
    for product in top_products_data:
        # Get latest order's item status for this product in current month
        latest_order = OrderTable.objects.filter(
            productid=product['productid'],
            salesid__sales_date__range=(start_date, end_date)
        ).order_by('-salesid__sales_date').select_related('salesid__itemstatusid').first()

        status = getattr(latest_order.salesid.itemstatusid, 'itemstat', 'Unknown') if latest_order else 'Unknown'
        badge_class = badge_map.get(status, 'text-bg-secondary')

        top_products.append({
            'name': product['productid__prodnameid__name'],
            'image_url': product.get('productid__productimage', ''),
            'quantity_sold': product['total_qty'],
            'price': product.get('productid__priceid__amount', 0),
            'status': status,
            'badge_class': badge_class,
        })

    # 4. Dashboard Metrics
    total_sales = sales.aggregate(total=Sum('total_price'))['total'] or 0
    new_orders = orders.count()
    total_customers = sales.values('customerid').distinct().count()

    # Context
    context = {
        'sales_labels': sales_labels,
        'sales_totals': sales_totals,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'total_sales': round(total_sales, 2),
        'new_orders': new_orders,
        'total_customers': total_customers,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'adminDashboard.html', context)

@login_required(login_url='adminLogin')
def addProduct(request):
    if request.method == 'POST':
        # Create or Edit Product
        product_form = ProductForm(request.POST, request.FILES)
        product_id = request.POST.get('productid')

        if product_id:  # Editing an existing product
            product = get_object_or_404(ProductTable, productid=product_id)
            product_form = ProductForm(request.POST, request.FILES, instance=product)
            if product_form.is_valid():
                product_form.save()
                return redirect('addProduct')  # Redirect after saving
        elif 'delete' in request.POST:  # Deleting a product
            product_id = request.POST.get('delete')
            product = get_object_or_404(ProductTable, productid=product_id)
            product.delete()
            return redirect('addProduct')  # Redirect after deletion
        else:  # Creating a new product
            if product_form.is_valid():
                product_form.save()
                return redirect('addProduct')  # Redirect after saving

    else:
        product_form = ProductForm()

    products = ProductTable.objects.all()

    context = {
        'product_form': product_form,
        'products': products,
        'edit_mode': False,  # Default is not in edit mode
    }

    # Check if we are editing a product
    product_id = request.GET.get('edit')  # Check URL for 'edit' parameter
    if product_id:
        product = get_object_or_404(ProductTable, productid=product_id)
        product_form = ProductForm(instance=product)
        context['product_form'] = product_form
        context['edit_mode'] = True  # Now we're in edit mode
        context['product_id'] = product_id  # Pass product ID to the template

    return render(request, 'addProduct.html', context)

@login_required(login_url='adminLogin')
def orderedItems(request):
    date_filter = request.GET.get('date')
    product_filter = request.GET.get('product')

    orders = OrderTable.objects.all().select_related(
        'productid__prodnameid',
        'productid__colorid',
        'sizeid',
        'priceid',
    ).order_by('-orderid')

    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            orders = orders.filter(salesid__sales_date=date_obj)
        except ValueError:
            pass  # Ignore invalid dates

    if product_filter:
        orders = orders.filter(productid__productid=product_filter)

    # Get product list for the dropdown
    products = ProductTable.objects.select_related('prodnameid', 'colorid').all()

    return render(request, 'orderItems.html', {
        'orders': orders,
        'products': products,
    })

@login_required(login_url='adminLogin')
def inventory(request):
    return render(request, 'inventory.html')

@login_required(login_url='adminLogin')
def analysis(request):
    return render(request, 'analysis.html')

@login_required(login_url='adminLogin')
def newProductName(request):
    edit_prodname = None
    form = None

    # Check if editing (GET param 'edit')
    edit_id = request.GET.get('edit')
    if edit_id:
        edit_prodname = get_object_or_404(ProdNameTable, pk=edit_id)
        form = ProdNameForm(instance=edit_prodname)
    else:
        form = ProdNameForm()

    if request.method == 'POST':
        # Delete request
        if 'delete_prodnameid' in request.POST:
            prodname = get_object_or_404(ProdNameTable, pk=request.POST['delete_prodnameid'])
            prodname.delete()
            messages.success(request, "Product name deleted.")
            return redirect('newProductName')

        # Update or Create request
        prodname_id = request.POST.get('prodnameid')
        if prodname_id:
            # Update
            prodname = get_object_or_404(ProdNameTable, pk=prodname_id)
            form = ProdNameForm(request.POST, instance=prodname)
            if form.is_valid():
                form.save()
                messages.success(request, "Product name updated.")
                return redirect('newProductName')
        else:
            # Create
            form = ProdNameForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Product name added.")
                return redirect('newProductName')

    product_names = ProdNameTable.objects.all().order_by('-prodnameid')
    return render(request, 'newProductName.html', {
        'form': form,
        'product_names': product_names,
        'edit_prodname': edit_prodname,
    })

@login_required(login_url='adminLogin')
def salesManagement(request):
    search_query = request.GET.get('search', '')

    sales_qs = SalesTable.objects.all() \
    .select_related('customerid', 'itemstatusid') \
    .annotate(
        status_order=Case(
            When(itemstatusid__itemstat='Pending', then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ) \
    .order_by('status_order', 'salesid')

    if search_query:
        # Search by order number or customer first/last name (case-insensitive)
        sales_qs = sales_qs.filter(
            Q(ordernumber__icontains=search_query) |
            Q(customerid__firstname__icontains=search_query) |
            Q(customerid__lastname__icontains=search_query)
        )

    paginator = Paginator(sales_qs, 10)  # 10 sales per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get IDs of sales in current page
    sales_ids = list(page_obj.object_list.values_list('salesid', flat=True))

    # Get payments related to these sales
    payments = PaymentTable.objects.filter(salesid__in=sales_ids).select_related('paystatid')

    # Prepare a dict of payments keyed by salesid (assuming one payment per sale)
    payment_dict = {}
    for payment in payments:
        payment_dict[payment.salesid_id] = payment  # map sale id to payment object

    # Prepare combined forms for each sale
    combined_forms = {}
    for sale in page_obj.object_list:
        payment = payment_dict.get(sale.salesid)
        if payment:
            initial_data = {
                'itemstatusid': sale.itemstatusid_id,
                'paystatid': payment.paystatid_id,
                'salesid': sale.salesid,
                'paymentid': payment.paymentid,
            }
            combined_forms[sale.salesid] = CombinedStatusForm(initial=initial_data)
        else:
            # If no payment found, just fill itemstatus and salesid
            initial_data = {
                'itemstatusid': sale.itemstatusid_id,
                'salesid': sale.salesid,
                # paymentid is required in the form, so you might want to handle this case accordingly
            }
            combined_forms[sale.salesid] = CombinedStatusForm(initial=initial_data)

    return render(request, 'salesManagement.html', {
        'page_obj': page_obj,
        'payments': payments,
        'combined_forms': combined_forms,  # pass combined forms instead of separate forms
        'search_query': search_query,
    })

@login_required(login_url='adminLogin')
def update_statuses(request):
    if request.method == 'POST':
        form = CombinedStatusForm(request.POST)
        if form.is_valid():
            salesid = form.cleaned_data.get('salesid')
            paymentid = form.cleaned_data.get('paymentid')
            itemstatusid = form.cleaned_data.get('itemstatusid')
            paystatid = form.cleaned_data.get('paystatid')

            try:
                if salesid and itemstatusid:
                    sale = get_object_or_404(SalesTable, pk=salesid)
                    sale.itemstatusid = itemstatusid
                    sale.save()

                if paymentid and paystatid:
                    payment = get_object_or_404(PaymentTable, pk=paymentid)
                    payment.paystatid = paystatid
                    payment.save()

                messages.success(request, "Status updated successfully!")
            except Exception as e:
                messages.error(request, f"Error updating status: {str(e)}")
        else:
            messages.error(request, "Invalid form data.")
    return redirect('salesManagement')

# DATA ANALYSIS
@login_required(login_url='adminLogin')
def salesMonitor(request):
    # Get current date
    today = date.today()
    sales_timeframe = request.GET.get('timeframe', 'month')
    
    # Dynamic date range based on timeframe
    if sales_timeframe == 'day':
        # Last 30 days
        start_date = today - timedelta(days=30)
        end_date = today
    elif sales_timeframe == 'week':
        # Last 12 weeks
        start_date = today - timedelta(weeks=12)
        end_date = today
    elif sales_timeframe == 'year':
        # Last 5 years
        start_date = date(today.year - 5, 1, 1)
        end_date = today
    else:  # month (default)
        # Last 12 months
        start_date = date(today.year - 1, today.month, 1)
        end_date = today
    
    # Filter orders and sales within date range
    orders = OrderTable.objects.filter(salesid__sales_date__range=(start_date, end_date))
    sales = SalesTable.objects.filter(sales_date__range=(start_date, end_date))

    # ========== SALES TRENDS ========== #
    if sales_timeframe == 'day':
        sales_data = sales.annotate(day=TruncDay('sales_date')) \
                    .values('day').annotate(total=Count('salesid')).order_by('day')
        timeframe_labels = [s['day'].strftime('%d %b') for s in sales_data]
    elif sales_timeframe == 'week':
        sales_data = sales.annotate(week=TruncWeek('sales_date')) \
                    .values('week').annotate(total=Count('salesid')).order_by('week')
        timeframe_labels = [s['week'].strftime('Week of %d %b') for s in sales_data]
    elif sales_timeframe == 'year':
        sales_data = sales.annotate(year=TruncYear('sales_date')) \
                    .values('year').annotate(total=Count('salesid')).order_by('year')
        timeframe_labels = [s['year'].strftime('%Y') for s in sales_data]
    else:  # month (default)
        sales_data = sales.annotate(month=TruncMonth('sales_date')) \
                    .values('month').annotate(total=Count('salesid')).order_by('month')
        timeframe_labels = [s['month'].strftime('%b %Y') for s in sales_data]

    # ========== MOST BOUGHT ANALYTICS ========== #
    # Calculate revenue for each color
    color_data = orders.values('productid__colorid__colorname') \
                    .annotate(
                        total_revenue=Sum(F('quantity') * F('priceid__amount'), output_field=DecimalField())
                    ).order_by('-total_revenue')

    # Calculate revenue for each design
    design_data = orders.values('productid__prodnameid__name') \
                    .annotate(
                        total_revenue=Sum(F('quantity') * F('priceid__amount'), output_field=DecimalField())
                    ).order_by('-total_revenue')

    # Calculate revenue for each size
    size_data = orders.values('sizeid__size') \
                    .annotate(
                        total_revenue=Sum(F('quantity') * F('priceid__amount'), output_field=DecimalField())
                    ).order_by('-total_revenue')

    # Calculate revenue for each product/color combo
    combo_data = orders.values('productid__prodnameid__name', 'productid__colorid__colorname') \
                    .annotate(
                        total_revenue=Sum(F('quantity') * F('priceid__amount'), output_field=DecimalField())
                    ).order_by('-total_revenue')

    # ========== AVERAGE ORDER VALUE (AOV) ========== #
    aov = sales.aggregate(avg_order=Avg('total_price'))['avg_order'] or 0

    # ========== CUSTOMER LIFETIME VALUE (CLTV) ========== #
    cltv_data = sales.values('customerid__firstname') \
                     .annotate(cltv=Sum('total_price')) \
                     .order_by('-cltv')[:5]  # top 5 customers

    cltv_labels = [entry['customerid__firstname'] for entry in cltv_data]
    cltv_totals = [float(entry['cltv']) for entry in cltv_data]  # Convert Decimal to float

    # ========== SALES TREND ANALYSIS ========== #
    linearx = np.arange(len(sales_data)).reshape(-1, 1)
    lineary = np.array([s['total'] for s in sales_data])
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

    # ========== OUTLIER DETECTION ========== #
    sales_values = [int(x) for x in lineary]  # Convert numpy ints to native int
    outliers = []

    if len(sales_values) >= 2:
        mean = statistics.mean(sales_values)
        stdev = statistics.stdev(sales_values)
        outliers = [timeframe_labels[i] for i, val in enumerate(sales_values)
                    if abs(val - mean) > 2 * stdev]

    # ========== CONTEXT FOR TEMPLATE ========== #
    context = {
        'color_labels': [c['productid__colorid__colorname'] for c in color_data],
        'color_totals': [float(c['total_revenue']) if c['total_revenue'] else 0 for c in color_data],

        'design_labels': [d['productid__prodnameid__name'] for d in design_data],
        'design_totals': [float(d['total_revenue']) if d['total_revenue'] else 0 for d in design_data],

        'size_labels': [s['sizeid__size'] for s in size_data],
        'size_totals': [float(s['total_revenue']) if s['total_revenue'] else 0 for s in size_data],

        'combo_labels': [f"{c['productid__prodnameid__name']}/{c['productid__colorid__colorname']}" for c in combo_data[:5]],
        'combo_totals': [float(c['total_revenue']) if c['total_revenue'] else 0 for c in combo_data[:5]],

        'sales_labels': timeframe_labels,
        'sales_totals': sales_values,

        'average_order_value': round(float(aov), 2),
        'cltv_labels': cltv_labels,
        'cltv_totals': cltv_totals,

        'sales_trend': trend,
        'outlier_periods': outliers,
    }

    return render(request, 'salesMonitor.html', context)
