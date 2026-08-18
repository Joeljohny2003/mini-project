from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
import razorpay
from .models import Product, Cart, CartItem, Order, Category
from .forms import ProductForm
from .forms import CheckoutForm

# Create your views here.

def home(request):

    featured_products = Product.objects.filter(
        available=True
    ).order_by('-created_at')[:8]

    categories = Category.objects.all()

    return render(
        request,
        'marketplace/home.html',
        {
            'featured_products': featured_products,
            'categories': categories,
        }
    )

def products(request):
    products_list = Product.objects.filter(available=True)
    categories = Category.objects.all()

    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()

    if query:
        products_list = products_list.filter(name__icontains=query)

    if category_id:
        products_list = products_list.filter(category_id=category_id)

    return render(
        request,
        'marketplace/products.html',
        {
            'products': products_list,
            'categories': categories,
            'query': query,
            'selected_category': category_id,
        }
    )

def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(
        request,
        'marketplace/product_details.html',
        {
            'product': product
        }
    )

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(
        request,
        'marketplace/register.html',
        {'form': form}
    )


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        return render(
            request,
            'marketplace/login.html',
            {'error': 'Invalid username or password.'}
        )

    return render(request, 'marketplace/login.html')


def user_logout(request):
    logout(request)
    return redirect('home')

def sell_item(request):

    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('products')

    else:
        form = ProductForm()

    return render(
        request,
        'marketplace/sell_item.html',
        {'form': form}
    )

def add_to_cart(request, product_id):

    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')

def cart(request):

    if not request.user.is_authenticated:
        return redirect('login')

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_items = cart.items.select_related('product')

    total = sum(
        item.total_price()
        for item in cart_items
    )

    return render(
        request,
        'marketplace/cart.html',
        {
            'cart': cart,
            'cart_items': cart_items,
            'total': total,
        }
    )

def checkout(request):

    if not request.user.is_authenticated:
        return redirect('login')

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_items = cart.items.select_related('product')

    if not cart_items.exists():
        return redirect('cart')

    total = sum(
        item.total_price()
        for item in cart_items
    )

    if request.method == 'POST':

        form = CheckoutForm(request.POST)

        if form.is_valid():

            order = form.save(commit=False)

            order.user = request.user
            order.total_amount = total

            # Cash on Delivery
            if order.payment_method == 'Cash on Delivery':

                order.payment_status = 'Pending'
                order.status = 'Confirmed'
                order.save()

                cart.items.all().delete()

                return redirect(
                    'order_success',
                    order_id=order.id
                )

            # Razorpay Online Payment
            elif order.payment_method == 'Razorpay':

                order.payment_status = 'Pending'
                order.status = 'Pending'
                order.save()

                client = razorpay.Client(
                    auth=(
                        settings.RAZORPAY_KEY_ID,
                        settings.RAZORPAY_KEY_SECRET
                    )
                )

                razorpay_order = client.order.create({
                    'amount': int(total * 100),
                    'currency': 'INR',
                    'payment_capture': 1
                })

                order.razorpay_order_id = razorpay_order['id']
                order.save()

                return render(
                    request,
                    'marketplace/payment.html',
                    {
                        'order': order,
                        'razorpay_order_id': razorpay_order['id'],
                        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                        'amount': int(total * 100),
                    }
                )

    else:
        form = CheckoutForm()

    return render(
        request,
        'marketplace/checkout.html',
        {
            'form': form,
            'cart_items': cart_items,
            'total': total,
        }
    )

def payment_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    payment_id = request.GET.get('razorpay_payment_id')
    razorpay_order_id = request.GET.get('razorpay_order_id')
    signature = request.GET.get('razorpay_signature')

    if not payment_id or not razorpay_order_id or not signature:
        return render(
            request,
            'marketplace/payment_failed.html',
            {
                'order': order,
                'message': 'Payment information is incomplete.'
            }
        )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    try:

        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

        order.razorpay_payment_id = payment_id
        order.razorpay_order_id = razorpay_order_id
        order.razorpay_signature = signature

        order.payment_status = 'Paid'
        order.status = 'Confirmed'

        order.save()

        # Remove purchased items from cart
        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            cart.items.all().delete()

        return redirect(
            'order_success',
            order_id=order.id
        )

    except razorpay.errors.SignatureVerificationError:

        order.payment_status = 'Failed'
        order.save()

        return render(
            request,
            'marketplace/payment_failed.html',
            {
                'order': order,
                'message': 'Payment verification failed.'
            }
        )


def order_success(request, order_id):

    if not request.user.is_authenticated:
        return redirect('login')

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        'marketplace/order_success.html',
        {
            'order': order
        }
    )

@login_required
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'marketplace/my_orders.html',
        {'orders': orders}
    )

@login_required
def my_listings(request):

    products = Product.objects.filter(
        seller=request.user
    ).order_by('-created_at')

    return render(
        request,
        'marketplace/my_listings.html',
        {'products': products}
    )

@login_required
def seller_dashboard(request):

    products = Product.objects.filter(
        seller=request.user
    ).order_by('-created_at')

    total_listings = products.count()

    active_listings = products.filter(
        available=True
    ).count()

    sold_listings = products.filter(
        available=False
    ).count()

    return render(
        request,
        'marketplace/seller_dashboard.html',
        {
            'products': products,
            'total_listings': total_listings,
            'active_listings': active_listings,
            'sold_listings': sold_listings,
        }
    )