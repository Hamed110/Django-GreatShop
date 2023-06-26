from django.core.exceptions import ObjectDoesNotExist

from .models import Cart, CartItem
from .views import _cart_id

def cart_quantity(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart__cart_id=cart, is_active=True)
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except ObjectDoesNotExist:
            cart_count = 0
    

    return dict(cart_quantity=cart_count)