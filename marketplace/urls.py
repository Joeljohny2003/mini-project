from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),

    path(
        'products/<int:product_id>/',
        views.product_details,
        name='product_details'
    ),

    path(
        'products/<int:product_id>/chat/',
        views.product_chat,
        name='product_chat'
    ),

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('delivery/register/', views.delivery_register, name='delivery_register'),
    path('delivery/login/', views.delivery_login, name='delivery_login'),
    path('delivery/', views.delivery_dashboard, name='delivery_dashboard'),

    path('sell/', views.sell_item, name='sell_item'),

    path('cart/', views.cart, name='cart'),

    path(
        'cart/add/<int:product_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path('checkout/', views.checkout, name='checkout'),

    path(
        'order-success/<int:order_id>/',
        views.order_success,
        name='order_success'
    ),

    path('my-orders/', views.my_orders, name='my_orders'),
    path('my-listings/', views.my_listings, name='my_listings'),

    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),

    path(
        'payment-success/<int:order_id>/',
        views.payment_success,
        name='payment_success'
    ),
]