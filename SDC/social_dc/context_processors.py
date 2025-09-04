# social_dc/context_processors.py

def cart_items_processor(request):
    cart_items = request.session.get('cart', [])

    total_price = 0
    for item in cart_items:
        try:
            item["subtotal"] = int(item["price"]) * int(item["quantity"])
        except (KeyError, ValueError, TypeError):
            item["subtotal"] = 0
        total_price += item["subtotal"]

    return {
        'cart_items': cart_items,
        'total_price': total_price,
    }
