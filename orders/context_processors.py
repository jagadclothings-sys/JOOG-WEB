from .models import Cart

def cart_context(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return {
            'user_cart': cart,
            'cart_total_items': cart.get_total_items(),
        }
    return {'user_cart': None, 'cart_total_items': 0}