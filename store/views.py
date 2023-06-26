from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q

from.models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id

from django.http import HttpResponse
def store(request, category_slug=None):

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
    else:
        products = Product.objects.filter(is_available=True)

    products_count = products.count()

    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'products_count': products_count,
    }
    
    return render(request, 'store/store.html', context)



def product_detail(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=product).exists()

        color_variations = product.variations.filter(variation_category='color', is_active=True)
        size_variations = product.variations.filter(variation_category='size', is_active=True)
        
    except Exception as e:
        raise e
    
    
    context = {
        'product': product,
        'in_cart': in_cart,
        'color_variations': color_variations,
        'size_variations': size_variations,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        search = request.GET.get('keyword')

        if search:
            products = Product.objects.order_by('created_date').filter(Q(product_name__icontains=search) | Q(description__icontains=search)).filter(is_available=True)
        

            products_count = products.count()

            context = {
                'products': products,
                'products_count': products_count,
            }

            return render(request, 'store/store.html', context)
        
        else:
            return redirect('store')
