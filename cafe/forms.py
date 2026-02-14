from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML
from crispy_forms.bootstrap import FormActions
from .models import UserProfile, Order, Review, Category, MenuItem, DeliveryAddress, Rating


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add required class to all required fields
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = 'required'
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' required-field'
                else:
                    field.widget.attrs['class'] = 'form-control required-field'
            
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'username',
            'email',
            'password1',
            'password2',
            FormActions(
                Submit('submit', 'Create Account', css_class='btn btn-primary btn-lg w-100')
            )
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image', 'phone', 'address', 'city', 'postal_code', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = 'required'


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = 'required'


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'phone', 'notes']
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your complete delivery address', 'required': 'required'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter your phone number', 'required': 'required'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Any special instructions (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = 'required'
                
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'delivery_address',
            'phone',
            'notes',
            FormActions(
                Submit('submit', 'Place Order', css_class='btn btn-success btn-lg w-100', id='submit-button')
            )
        )


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience with this item...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'rating',
            'comment',
            FormActions(
                Submit('submit', 'Submit Review', css_class='btn btn-primary')
            )
        )


# Custom Admin Forms
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'icon']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'icon': forms.TextInput(attrs={
                'placeholder': 'e.g., fa-pizza-slice, fa-burger, fa-coffee',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('slug', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'description',
            Row(
                Column('image', css_class='form-group col-md-6 mb-0'),
                Column('icon', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Save Category', css_class='btn btn-primary')
        )


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = [
            'name', 'slug', 'category', 'price', 'discount', 
            'description', 'ingredients', 'image', 'image_url',
            'available', 'is_featured', 'preparation_time'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'ingredients': forms.Textarea(attrs={'rows': 2}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-8 mb-0'),
                Column('slug', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('category', css_class='form-group col-md-6 mb-0'),
                Column('preparation_time', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('price', css_class='form-group col-md-4 mb-0'),
                Column('discount', css_class='form-group col-md-4 mb-0'),
                Column(
                    Field('available', css_class='form-check-input'),
                    Field('is_featured', css_class='form-check-input'),
                    css_class='form-group col-md-4 mb-0'
                ),
                css_class='form-row'
            ),
            'description',
            'ingredients',
            Row(
                Column('image', css_class='form-group col-md-6 mb-0'),
                Column('image_url', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Save Menu Item', css_class='btn btn-primary')
        )

class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ['label', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'phone', 'is_default']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Home, Office', 'required': 'required'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address', 'required': 'required'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartment, suite, etc. (optional)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City', 'required': 'required'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State', 'required': 'required'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal code', 'required': 'required'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number', 'required': 'required'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = 'required'
                
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('label', css_class='form-group col-md-6 mb-3'),
                Column('phone', css_class='form-group col-md-6 mb-3'),
            ),
            'address_line_1',
            'address_line_2',
            Row(
                Column('city', css_class='form-group col-md-4 mb-3'),
                Column('state', css_class='form-group col-md-4 mb-3'),
                Column('postal_code', css_class='form-group col-md-4 mb-3'),
            ),
            Field('is_default', css_class='form-check'),
            FormActions(
                Submit('submit', 'Save Address', css_class='btn btn-primary')
            )
        )


class CouponForm(forms.Form):
    coupon_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter coupon code',
            'style': 'text-transform: uppercase;'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('coupon_code', css_class='form-group col-md-8 mb-0'),
                Column(
                    Submit('apply', 'Apply Coupon', css_class='btn btn-success'),
                    css_class='form-group col-md-4 mb-0 d-flex align-items-end'
                ),
            )
        )


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'rating',
            FormActions(
                Submit('submit', 'Submit Rating', css_class='btn btn-primary')
            )
        )