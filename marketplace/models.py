from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    CONDITION_CHOICES = [
        ("New", "New"),
        ("Like New", "Like New"),
        ("Good", "Good"),
        ("Fair", "Fair"),
    ]

    name = models.CharField(max_length=200)

    company = models.CharField(max_length=150, blank=True, default="")

    antiquity = models.PositiveIntegerField(
        default=0,
        help_text="Age of the item in years"
    )

    seller = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='products_for_sale'
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES
    )

    location = models.CharField(max_length=200)

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    image2 = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        help_text="Additional product photo 2"
    )

    image3 = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        help_text="Additional product photo 3"
    )

    serial_number = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text="Serial or model number of the product"
    )

    purchase_proof = models.ImageField(
        upload_to="products/purchase_proof/",
        blank=True,
        null=True,
        help_text="Upload purchase bill, invoice, or receipt as proof of ownership"
    )

    available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ChatMessage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    buyer = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='buyer_chat_messages'
    )
    sender = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='sent_chat_messages'
    )
    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Chat about {self.product.name} from {self.sender.username}"


class DeliveryPerson(models.Model):
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='delivery_profile'
    )
    phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Cart(models.Model):
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def total_price(self):
        return self.product.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )

    delivery_person = models.ForeignKey(
        DeliveryPerson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries'
    )

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)

    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    delivery_method = models.CharField(
        max_length=50,
        default="Standard Delivery"
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
     max_length=50,
     default="Cash on Delivery"
    )

    payment_status = models.CharField(
     max_length=20,
     default="Pending"
    )

    razorpay_order_id = models.CharField(
     max_length=100,
     blank=True,
     null=True
    )

    razorpay_payment_id = models.CharField(
     max_length=100,
     blank=True,
     null=True
    )

    razorpay_signature = models.CharField(
     max_length=255,
     blank=True,
     null=True
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"