from .models import Cart, Category


def cart_context(request):
    """Makes the current user's cart item count and categories
    available to every template."""

    count = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            count = sum(item.quantity for item in cart.items.all())

    return {
        'nav_cart_count': count,
        'nav_categories': Category.objects.all(),
    }