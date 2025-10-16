from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views
from .views import OrderRequestView, VerifyOrderOTPView 

urlpatterns = [
    path('', views.home, name="home"),
    path('aboutus/', views.aboutus, name="aboutus"),
    path('product/', views.product, name="product"),
    path('contacts/', views.contacts, name="contacts"),
    path('faq/', views.faq, name="faq"),
    path('productPage/<int:productID>', views.productPage, name="productPage"),
    path('adminRegistration/', views.adminRegister, name="adminRegister"),
    path('adminLogin/', views.adminLogin, name="adminLogin"),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('orderSuccess/', views.order_success, name="order_success"),

    #OTP
    path('checkout/', views.checkout, name='checkout'),
    path('send-otp/', views.OrderRequestView.as_view(), name='send_otp'),
    path('verify-otp/', views.VerifyOrderOTPView.as_view(), name='verify_otp'),

    # CART FUNCTIONS
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:product_id>/<str:size>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('remove-from-cart/<int:product_id>/<str:size>/', views.remove_from_cart, name='remove_from_cart'),

    # ADD PRODUCT
    path('adminProduct/', views.addProduct, name="addProduct"),
    path('adminDashboard/', views.adminDashboard, name='adminDashboard'),
    path('newProductName/', views.newProductName, name="newProductName"),

    #Admin URLS 
    path('orderedItems/', views.orderedItems, name="orderedItems"),
    path('salesMonitoring/', views.salesMonitor, name="salesMonitor"),
    path('analysis/', views.analysis, name="analysis"),
    path('salesManagement/', views.salesManagement, name="salesManagement"),
    path('salesManagement/update-statuses/', views.update_statuses, name='update_statuses'),
]