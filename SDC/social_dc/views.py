from django.shortcuts import render

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
    return render(request, 'product.html')

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
