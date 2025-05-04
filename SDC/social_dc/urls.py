from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('aboutus/', views.aboutus, name="aboutus"),
    path('product/', views.product, name="product"),
    path('contacts/', views.contacts, name="contacts"),
    path('faq/', views.faq, name="faq"),
    path('cart/', views.cart, name="cart"),
    path('productPage/<int:productID>', views.productPage, name="productPage"),
    path('adminRegistration/', views.adminRegistration, name="register"),
    path('adminLogin/', views.adminLogin, name="login"),
    path('orderedItems/', views.orderedItems, name="orderedItems"),
    path('paymentAssessment/', views.paymentAss, name="paymentAss"),
    path('salesMonitoring/', views.salesMonitor, name="salesMonitor"),
    path('inventory/', views.inventory, name="inventory"),
    path('productCreation/', views.productCreation, name="productCreation"),
    path('variantCreation/', views.variantCreation, name="variantCreation"),
    path('analysis/', views.analysis, name="analysis"),
    path('add-to-cart/<int:productID>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/<str:size>/<str:color>/', views.remove_from_cart, name='remove_from_cart'),
]