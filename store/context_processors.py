from store.models import Category,Cart,CartItem
from store.views import _cart_id

def menu_links(request) :
    links = Category.objects.all()
    return dict(links=links)

def counter(request):
    item_count = 0

    if 'admin' in request.path:
        return {}
    else:
        cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
        if cart:
            cart_items = CartItem.objects.filter(cart=cart)
            for cart_item in cart_items:
                item_count += cart_item.quantity

    return {'item_count': item_count}
