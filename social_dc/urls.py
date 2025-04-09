from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('aboutus/', views.aboutus, name="aboutus"),
    path('product/', views.product, name="product"),
    path('contacts/', views.contacts, name="contacts"),
    path('cart/', views.cart, name="cart"),
    path('adminRegistration/', views.adminRegistration, name="register"),
    path('adminLogin/', views.adminLogin, name="login"),
    path('orderedItems/', views.orderedItems, name="orderedItems"),
    path('paymentAssessment/', views.paymentAss, name="paymentAss"),
    path('salesMonitoring/', views.salesMonitor, name="salesMonitoring"),
    path('inventory/', views.inventory, name="inventory"),
]