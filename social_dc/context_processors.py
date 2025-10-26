# social_dc/context_processors.py

def cart_items_processor(request):
    cart_items = request.session.get('cart', [])

    total_item_count = 0
    total_price = 0
    unique_products = set()

    for item in cart_items:
        try:
            item["subtotal"] = int(item["price"]) * int(item["quantity"])
        except (KeyError, ValueError, TypeError):
            item["subtotal"] = 0
        total_price += item["subtotal"]
        
        # Count unique products by product_name (same across all sizes/colors)
        if "product_name" in item:
            unique_products.add(item["product_name"])
    
    total_item_count = len(unique_products)  # Count unique products only

    return {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_item_count': total_item_count, 
    }