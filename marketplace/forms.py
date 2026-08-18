from django import forms
from .models import Product, Order


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            'name',
            'category',
            'description',
            'price',
            'condition',
            'location',
            'image',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),

            'category': forms.Select(attrs={
                'class': 'form-control'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your product',
                'rows': 5
            }),

            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price'
            }),

            'condition': forms.Select(attrs={
                'class': 'form-control'
            }),

            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your location'
            }),

            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'full_name',
            'phone',
            'address',
            'city',
            'state',
            'pincode',
            'delivery_method',
            'payment_method',
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Full Name',
                'class': 'form-control',
            }),

            'phone': forms.TextInput(attrs={
                'placeholder': 'Phone Number',
                'class': 'form-control',
            }),

            'address': forms.Textarea(attrs={
                'placeholder': 'Delivery Address',
                'class': 'form-control',
                'rows': 4,
            }),

            'city': forms.TextInput(attrs={
                'placeholder': 'City',
                'class': 'form-control',
            }),

            'state': forms.TextInput(attrs={
                'placeholder': 'State',
                'class': 'form-control',
            }),

            'pincode': forms.TextInput(attrs={
                'placeholder': 'PIN Code',
                'class': 'form-control',
            }),

            'delivery_method': forms.Select(
                choices=[
                    ('Standard Delivery', 'Standard Delivery'),
                    ('Express Delivery', 'Express Delivery'),
                    ('Pickup', 'Pickup'),
                ],
                attrs={
                    'class': 'form-control',
                }
            ),

            'payment_method': forms.Select(
                choices=[
                    ('Cash on Delivery', 'Cash on Delivery'),
                    ('Razorpay', 'Online Payment (Razorpay)'),
                    ],
                attrs={
                    'class': 'form-control',
                }
            ),
        }