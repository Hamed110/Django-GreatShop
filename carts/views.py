from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from store.models import Product, Variation
from carts.models import Cart, CartItem


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_to_cart(requset, product_id):

    if requset.method == 'POST':

        product = Product.objects.get(id=product_id, is_available=True)
        product_variations = list()

        for item in requset.POST:
            key = item
            value = requset.POST.get(key)
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                if variation:
                    product_variations.append(variation)
            except:
                pass
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(requset))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(requset))


        existing_variations = list()
        ids = list()
        does_cart_item_exist = CartItem.objects.filter(cart=cart, product=product).exists()

        if does_cart_item_exist:
            existing_cart_items = CartItem.objects.filter(cart=cart, product=product)

            for item in existing_cart_items:
                variations = item.variations.all()
                existing_variations.append(list(variations))
                ids.append(item.id)

            if product_variations in existing_variations:

                index = existing_variations.index(product_variations)
                id = ids[index]
                item = CartItem.objects.get(id=id, cart=cart, product=product)
                item.quantity += 1
                item.save()

            else:
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=1
                )
                if len(product_variations) > 0:
                    for item in product_variations:
                        cart_item.variations.add(item)


        else:
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=1
            )
            if len(product_variations) > 0:
                for item in product_variations:
                    cart_item.variations.add(item)


    return redirect('cart')



def remove_from_cart(request, product_id, cart_item_id):

    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

    cart_item.delete()

    return redirect('cart')



def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (total * 9)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    
    context = {
        'cart_items': cart_items,
        'quantity': quantity,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'cart/cart.html', context)
