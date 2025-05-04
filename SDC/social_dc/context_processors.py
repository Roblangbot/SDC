# social_dc/context_processors.py
def cart_items_processor(request):
    return {
        'cart_items': request.session.get('cart', [])
    }