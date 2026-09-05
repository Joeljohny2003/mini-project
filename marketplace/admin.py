from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, ChatMessage, DeliveryPerson

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(ChatMessage)
admin.site.register(DeliveryPerson)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'full_name',
        'total_amount',
        'delivery_method',
        'payment_method',
        'payment_status',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'payment_status',
        'delivery_method',
        'payment_method',
    )

    search_fields = (
        'full_name',
        'phone',
        'user__username',
    )

    ordering = ('-created_at',)