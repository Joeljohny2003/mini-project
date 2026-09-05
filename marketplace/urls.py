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

    path(
        'admin-login/',
        views.admin_login,
        name='admin_login'
    ),
    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),
    path(
        'panel/products/',
        views.admin_products,
        name='admin_products'
    ),
    path(
        'panel/products/<int:product_id>/edit/',
        views.admin_product_edit,
        name='admin_product_edit'
    ),
    path(
        'panel/products/<int:product_id>/delete/',
        views.admin_product_delete,
        name='admin_product_delete'
    ),
    path(
        'panel/products/<int:product_id>/toggle/',
        views.admin_product_toggle,
        name='admin_product_toggle'
    ),
    path(
        'panel/orders/',
        views.admin_orders,
        name='admin_orders'
    ),
    path(
        'panel/orders/<int:order_id>/status/',
        views.admin_order_status,
        name='admin_order_status'
    ),
    path(
        'panel/users/',
        views.admin_users,
        name='admin_users'
    ),
    path(
        'panel/users/<int:user_id>/toggle/',
        views.admin_user_toggle,
        name='admin_user_toggle'
    ),
    path(
        'panel/users/<int:user_id>/edit/',
        views.admin_user_edit,
        name='admin_user_edit'
    ),
    path(
        'panel/users/<int:user_id>/delete/',
        views.admin_user_delete,
        name='admin_user_delete'
    ),
    path(
        'panel/categories/',
        views.admin_categories,
        name='admin_categories'
    ),
    path(
        'panel/categories/<int:category_id>/delete/',
        views.admin_category_delete,
        name='admin_category_delete'
    ),
    path(
        'panel/delivery/',
        views.admin_delivery,
        name='admin_delivery'
    ),
    path(
        'panel/delivery/<int:delivery_id>/toggle/',
        views.admin_delivery_toggle,
        name='admin_delivery_toggle'
    ),

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

    path(
        'my-orders/remove/<int:order_id>/',
        views.remove_order,
        name='remove_order'
    ),

    path(
        'my-orders/restore/<int:order_id>/',
        views.restore_order,
        name='restore_order'
    ),

    path('my-listings/', views.my_listings, name='my_listings'),

    path(
        'my-listings/unlist/<int:product_id>/',
        views.unlist_product,
        name='unlist_product'
    ),

    path(
        'my-listings/remove/<int:product_id>/',
        views.remove_product,
        name='remove_product'
    ),

    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),

    path(
        'payment-success/<int:order_id>/',
        views.payment_success,
        name='payment_success'
    ),

    path('visual-search/', views.visual_search, name='visual_search'),
]