# utils.py
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import PendingOrder


def enrich_cart(session):
    cart_items = session.get('cart', [])
    total_price = 0
    for item in cart_items:
        item['subtotal'] = int(item['price']) * int(item['quantity'])
        total_price += item['subtotal']
    return cart_items, total_price

def generate_otp(length=6):
    return get_random_string(length=length, allowed_chars='0123456789')

def send_order_otp(email, otp):
    subject = 'Your Order OTP'
    message = f'Your OTP for order confirmation is: {otp}'
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [email])

def cleanup_expired_otps():
    """Delete all expired PendingOrder entries."""
    expiry_minutes = 10  # adjust if needed
    cutoff = timezone.now() - timedelta(minutes=expiry_minutes)
    deleted, _ = PendingOrder.objects.filter(created_at__lt=cutoff).delete()
    print(f"🧹 Cleaned up {deleted} expired OTPs.")