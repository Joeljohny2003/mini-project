from django import forms
from django.contrib.auth.models import User
from .models import Product, Order, DeliveryPerson


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            'name',
            'company',
            'antiquity',
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

            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company or brand'
            }),

            'antiquity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Age in years',
                'min': 0
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


class DeliveryRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Choose a username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Create a password'
    }))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm your password'
    }))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone number'
    }))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
            raise forms.ValidationError('Passwords do not match.')
        if User.objects.filter(username=cleaned_data.get('username')).exists():
            raise forms.ValidationError('That username is already in use.')
        return cleaned_data