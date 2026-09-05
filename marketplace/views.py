from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.models import Q, Count, Sum
from functools import wraps
from decimal import Decimal
import razorpay
from .models import Product, Cart, CartItem, Order, OrderItem, Category, ChatMessage, DeliveryPerson
from .forms import ProductForm
from .forms import CheckoutForm, DeliveryRegistrationForm, AdminUserEditForm
from .visual_search import find_similar_products

# Create your views here.


def customer_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        if DeliveryPerson.objects.filter(user=request.user, is_active=True).exists():
            return redirect('delivery_dashboard')
        return view(request, *args, **kwargs)
    return wrapped

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
    company = request.GET.get('company', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    min_antiquity = request.GET.get('min_antiquity', '').strip()
    max_antiquity = request.GET.get('max_antiquity', '').strip()

    if query:
        products_list = products_list.filter(name__icontains=query)

    if category_id:
        products_list = products_list.filter(category_id=category_id)

    if company:
        products_list = products_list.filter(
            Q(company__icontains=company) | Q(name__icontains=company)
        )

    if min_price:
        products_list = products_list.filter(price__gte=min_price)

    if max_price:
        products_list = products_list.filter(price__lte=max_price)

    if min_antiquity:
        products_list = products_list.filter(antiquity__gte=min_antiquity)

    if max_antiquity:
        products_list = products_list.filter(antiquity__lte=max_antiquity)

    return render(
        request,
        'marketplace/products.html',
        {
            'products': products_list,
            'categories': categories,
            'query': query,
            'selected_category': category_id,
            'company': company,
            'min_price': min_price,
            'max_price': max_price,
            'min_antiquity': min_antiquity,
            'max_antiquity': max_antiquity,
        }
    )

def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    similar_products = list(
        Product.objects.filter(
            available=True,
            category=product.category,
        ).exclude(id=product.id).order_by('-created_at')[:4]
    )

    messages = ChatMessage.objects.none()
    if request.user.is_authenticated and product.seller:
        if request.user == product.seller:
            messages = ChatMessage.objects.filter(product=product)
        else:
            messages = ChatMessage.objects.filter(
                product=product,
                buyer=request.user
            )

    return render(
        request,
        'marketplace/product_details.html',
        {
            'product': product,
            'similar_products': similar_products,
            'chat_messages': messages,
        }
    )


@customer_required
def product_chat(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not product.seller:
        return redirect('product_details', product_id=product.id)

    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        buyer = request.user
        if request.user == product.seller:
            buyer_id = request.POST.get('buyer_id', '').strip()
            buyer = get_object_or_404(User, id=buyer_id)
            if not ChatMessage.objects.filter(product=product, buyer=buyer).exists():
                return redirect('product_details', product_id=product.id)

        if message and buyer != product.seller:
            ChatMessage.objects.create(
                product=product,
                buyer=buyer,
                sender=request.user,
                message=message
            )

    return redirect('product_details', product_id=product.id)

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

        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect('admin_dashboard')

        if user is not None and not DeliveryPerson.objects.filter(user=user).exists():
            login(request, user)
            return redirect('home')

        if user is not None and DeliveryPerson.objects.filter(user=user).exists():
            error = 'This is a delivery account. Please use Delivery sign in.'
        else:
            error = 'Invalid username or password.'

        return render(
            request,
            'marketplace/login.html',
            {'error': error}
        )

    return render(request, 'marketplace/login.html')


def user_logout(request):
    logout(request)
    return redirect('home')


def delivery_register(request):
    if request.user.is_authenticated and not DeliveryPerson.objects.filter(user=request.user).exists():
        return redirect('home')

    if request.method == 'POST':
        form = DeliveryRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            DeliveryPerson.objects.create(
                user=user,
                phone=form.cleaned_data['phone']
            )
            login(request, user)
            return redirect('delivery_dashboard')
    else:
        form = DeliveryRegistrationForm()

    return render(request, 'marketplace/delivery_register.html', {'form': form})


def delivery_login(request):
    if request.user.is_authenticated and not DeliveryPerson.objects.filter(user=request.user).exists():
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user and DeliveryPerson.objects.filter(user=user, is_active=True).exists():
            login(request, user)
            return redirect('delivery_dashboard')

        return render(request, 'marketplace/delivery_login.html', {
            'error': 'Invalid delivery account details.'
        })

    return render(request, 'marketplace/delivery_login.html')


def delivery_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('delivery_login')

    delivery_person = get_object_or_404(
        DeliveryPerson,
        user=request.user,
        is_active=True
    )

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        order = get_object_or_404(Order, id=order_id)

        if action == 'claim' and order.status == 'Confirmed' and not order.delivery_person:
            order.delivery_person = delivery_person
            order.save(update_fields=['delivery_person'])
        elif order.delivery_person_id == delivery_person.id:
            if action == 'pickup' and order.status == 'Confirmed':
                order.status = 'Shipped'
                order.save(update_fields=['status'])
            elif action == 'deliver' and order.status == 'Shipped':
                order.status = 'Delivered'
                order.save(update_fields=['status'])

        return redirect('delivery_dashboard')

    available_orders = Order.objects.filter(
        status='Confirmed',
        delivery_person__isnull=True
    ).select_related('user').order_by('created_at')
    assigned_orders = Order.objects.filter(
        delivery_person=delivery_person
    ).select_related('user').order_by('-created_at')

    return render(request, 'marketplace/delivery_dashboard.html', {
        'delivery_person': delivery_person,
        'available_orders': available_orders,
        'assigned_orders': assigned_orders,
    })

def sell_item(request):

    if not request.user.is_authenticated:
        return redirect('login')
    if DeliveryPerson.objects.filter(user=request.user, is_active=True).exists():
        return redirect('delivery_dashboard')

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
    if DeliveryPerson.objects.filter(user=request.user, is_active=True).exists():
        return redirect('delivery_dashboard')

    product = get_object_or_404(Product, id=product_id, available=True)

    if product.seller:
        if product.seller_id == request.user.id:
            messages.error(request, 'You cannot buy or add your own listing to the cart.')
            return redirect('product_details', product_id=product.id)

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
    if DeliveryPerson.objects.filter(user=request.user, is_active=True).exists():
        return redirect('delivery_dashboard')

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_items = cart.items.select_related('product').filter(
        product__available=True
    ).exclude(
        product__seller=request.user
    )

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
    if DeliveryPerson.objects.filter(user=request.user, is_active=True).exists():
        return redirect('delivery_dashboard')

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_items = cart.items.select_related('product').filter(
        product__available=True
    ).exclude(
        product__seller=request.user
    )

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

            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=item.product.price,
                )
                for item in cart_items
            ]

            # Cash on Delivery
            if order.payment_method == 'Cash on Delivery':

                order.payment_status = 'Pending'
                order.status = 'Confirmed'
                order.save()
                OrderItem.objects.bulk_create(order_items)

                Product.objects.filter(
                    id__in=cart_items.values('product_id')
                ).update(available=False)

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
                OrderItem.objects.bulk_create(order_items)

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
            Product.objects.filter(
                id__in=cart.items.filter(
                    product__available=True
                ).values('product_id')
            ).update(available=False)
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

@customer_required
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user,
        visible_to_user=True
    ).order_by('-created_at')

    hidden_orders = Order.objects.filter(
        user=request.user,
        visible_to_user=False
    ).order_by('-created_at')

    return render(
        request,
        'marketplace/my_orders.html',
        {'orders': orders, 'hidden_orders': hidden_orders}
    )


@customer_required
def remove_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )
        order.visible_to_user = False
        order.save(update_fields=['visible_to_user'])

    return redirect('my_orders')


@customer_required
def restore_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )
        order.visible_to_user = True
        order.save(update_fields=['visible_to_user'])

    return redirect('my_orders')

@customer_required
def my_listings(request):

    products = Product.objects.filter(
        seller=request.user
    ).order_by('-created_at')

    return render(
        request,
        'marketplace/my_listings.html',
        {'products': products}
    )


@customer_required
def unlist_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(
            Product,
            id=product_id,
            seller=request.user
        )
        product.available = not product.available
        product.save(update_fields=['available'])
        state = 'unlisted' if not product.available else 're-listed'
        messages.success(request, f'Product "{product.name}" {state}.')
    return redirect('my_listings')


@customer_required
def remove_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(
            Product,
            id=product_id,
            seller=request.user
        )
        name = product.name
        if CartItem.objects.filter(product=product).exists():
            CartItem.objects.filter(product=product).delete()
        product.delete()
        messages.success(request, f'Listing "{name}" removed.')
    return redirect('my_listings')

@customer_required
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


def visual_search(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if DeliveryPerson.objects.filter(user=request.user, is_active=True).exists():
        return redirect('delivery_dashboard')

    results = []
    uploaded_image_url = None
    error = None

    if request.method == 'POST' and request.FILES.get('search_image'):
        search_image = request.FILES['search_image']

        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
        if search_image.content_type not in allowed_types:
            error = 'Please upload a valid image file (JPEG, PNG, WebP, or GIF).'
        elif search_image.size > 10 * 1024 * 1024:
            error = 'Image file must be under 10 MB.'
        else:
            try:
                import base64
                search_image.seek(0)
                uploaded_image_url = (
                    'data:' + search_image.content_type + ';base64,'
                    + base64.b64encode(search_image.read()).decode()
                )
                search_image.seek(0)
                results = find_similar_products(search_image, top_n=8)
            except Exception as e:
                import traceback
                traceback.print_exc()
                error = 'Something went wrong while analysing the image. Please try another.'

    return render(
        request,
        'marketplace/visual_search.html',
        {
            'results': results,
            'uploaded_image_url': uploaded_image_url,
            'error': error,
        }
    )


# ---------------------------------------------------------------
# ADMIN MODULE
# ---------------------------------------------------------------

def admin_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'You do not have admin access.')
            return redirect('admin_login')
        return view(request, *args, **kwargs)
    return wrapped


def admin_login(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect('admin_dashboard')

        error = 'Invalid admin credentials. Admin accounts are marked as staff.'
        return render(request, 'marketplace/admin_login.html', {'error': error})

    return render(request, 'marketplace/admin_login.html')


@admin_required
def admin_dashboard(request):

    total_products = Product.objects.count()
    available_products = Product.objects.filter(available=True).count()
    sold_products = Product.objects.filter(available=False).count()
    total_users = User.objects.filter(is_staff=False).count()

    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    confirmed_orders = Order.objects.filter(status='Confirmed').count()
    shipped_orders = Order.objects.filter(status='Shipped').count()
    delivered_orders = Order.objects.filter(status='Delivered').count()
    cancelled_orders = Order.objects.filter(status='Cancelled').count()

    total_revenue = Order.objects.filter(
        status__in=['Confirmed', 'Shipped', 'Delivered'],
        payment_status='Paid'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    pending_products = Product.objects.filter(available=True).order_by('-created_at')[:8]
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:8]
    recent_users = User.objects.filter(is_staff=False).order_by('-date_joined')[:8]
    recent_deliveries = DeliveryPerson.objects.select_related('user')[:8]

    return render(
        request,
        'marketplace/admin_dashboard.html',
        {
            'total_products': total_products,
            'available_products': available_products,
            'sold_products': sold_products,
            'total_users': total_users,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'confirmed_orders': confirmed_orders,
            'shipped_orders': shipped_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue': total_revenue,
            'pending_products': pending_products,
            'recent_orders': recent_orders,
            'recent_users': recent_users,
            'recent_deliveries': recent_deliveries,
        }
    )


@admin_required
def admin_products(request):
    products = Product.objects.select_related('seller', 'category').order_by('-created_at')

    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    category_id = request.GET.get('category', '').strip()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(company__icontains=query) | Q(seller__username__icontains=query)
        )
    if status:
        if status == 'available':
            products = products.filter(available=True)
        elif status == 'sold':
            products = products.filter(available=False)
    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()

    return render(
        request,
        'marketplace/admin_products.html',
        {
            'products': products,
            'categories': categories,
            'query': query,
            'status': status,
            'selected_category': category_id,
        }
    )


@admin_required
def admin_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('admin_products')
    else:
        form = ProductForm(instance=product)

    categories = Category.objects.all()
    return render(
        request,
        'marketplace/admin_product_edit.html',
        {
            'form': form,
            'product': product,
            'categories': categories,
        }
    )


@admin_required
def admin_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully.')
    return redirect('admin_products')


@admin_required
def admin_product_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.available = not product.available
        product.save(update_fields=['available'])
        state = 'activated' if product.available else 'deactivated'
        messages.success(request, f'Product "{product.name}" {state}.')
    return redirect('admin_products')


@admin_required
def admin_orders(request):
    orders = Order.objects.select_related('user', 'delivery_person').order_by('-created_at')

    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    payment_filter = request.GET.get('payment', '').strip()

    if query:
        orders = orders.filter(
            Q(id__icontains=query)
            | Q(full_name__icontains=query)
            | Q(user__username__icontains=query)
            | Q(phone__icontains=query)
        )
    if status_filter:
        orders = orders.filter(status=status_filter)
    if payment_filter:
        orders = orders.filter(payment_status=payment_filter)

    return render(
        request,
        'marketplace/admin_orders.html',
        {
            'orders': orders,
            'query': query,
            'status_filter': status_filter,
            'payment_filter': payment_filter,
            'STATUS_CHOICES': Order.STATUS_CHOICES,
            'payment_choices': ['Pending', 'Paid', 'Failed'],
        }
    )


@admin_required
def admin_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status', '').strip()
        if new_status in [choice[0] for choice in Order.STATUS_CHOICES]:
            order.status = new_status
            order.save(update_fields=['status'])
            messages.success(request, f'Order #{order.id} marked as {new_status}.')
    return redirect('admin_orders')


@admin_required
def admin_users(request):
    users = User.objects.filter(is_staff=False).order_by('-date_joined')

    query = request.GET.get('q', '').strip()
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    user_data = []
    for user in users:
        user_data.append({
            'user': user,
            'listings_count': user.products_for_sale.count(),
            'orders_count': Order.objects.filter(user=user).count(),
            'is_delivery': DeliveryPerson.objects.filter(user=user).exists(),
        })

    return render(
        request,
        'marketplace/admin_users.html',
        {
            'user_data': user_data,
            'query': query,
        }
    )


@admin_required
def admin_user_toggle(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        state = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User "{user.username}" {state}.')
    return redirect('admin_users')


@admin_required
def admin_user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST' and not user.is_superuser:
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" deleted.')
    return redirect('admin_users')


@admin_required
def admin_user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user.username}" updated successfully.')
            return redirect('admin_users')
    else:
        form = AdminUserEditForm(instance=user)

    delivery_info = None
    if DeliveryPerson.objects.filter(user=user).exists():
        delivery_info = DeliveryPerson.objects.get(user=user)

    return render(
        request,
        'marketplace/admin_user_edit.html',
        {
            'form': form,
            'user_being_edited': user,
            'delivery_info': delivery_info,
        }
    )


@admin_required
def admin_categories(request):
    categories = Category.objects.annotate(
        product_count=Count('product')
    ).order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name and not Category.objects.filter(name__iexact=name).exists():
            Category.objects.create(name=name)
            messages.success(request, f'Category "{name}" added.')
        elif name:
            messages.error(request, f'Category "{name}" already exists.')
        return redirect('admin_categories')

    return render(
        request,
        'marketplace/admin_categories.html',
        {'categories': categories}
    )


@admin_required
def admin_category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        name = category.name
        if Product.objects.filter(category=category).exists():
            messages.error(request, f'Cannot delete "{name}" because it has products assigned.')
        else:
            category.delete()
            messages.success(request, f'Category "{name}" deleted.')
    return redirect('admin_categories')


@admin_required
def admin_delivery(request):
    delivery_people = DeliveryPerson.objects.select_related('user').all()

    delivery_data = []
    for person in delivery_people:
        delivery_data.append({
            'person': person,
            'deliveries_count': Order.objects.filter(delivery_person=person).count(),
            'delivered_count': Order.objects.filter(delivery_person=person, status='Delivered').count(),
            'active_assignments': Order.objects.filter(
                delivery_person=person,
                status__in=['Confirmed', 'Shipped']
            ).count(),
        })

    return render(
        request,
        'marketplace/admin_delivery.html',
        {'delivery_data': delivery_data}
    )


@admin_required
def admin_delivery_toggle(request, delivery_id):
    person = get_object_or_404(DeliveryPerson, id=delivery_id)
    if request.method == 'POST':
        person.is_active = not person.is_active
        person.save(update_fields=['is_active'])
        state = 'activated' if person.is_active else 'deactivated'
        messages.success(request, f'Delivery person "{person.user.username}" {state}.')
    return redirect('admin_delivery')