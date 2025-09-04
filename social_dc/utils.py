# utils.py
def enrich_cart(session):
    cart_items = session.get('cart', [])
    total_price = 0
    for item in cart_items:
        item['subtotal'] = int(item['price']) * int(item['quantity'])
        total_price += item['subtotal']
    return cart_items, total_price
