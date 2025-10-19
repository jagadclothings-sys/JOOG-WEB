from django import forms
from django.forms import inlineformset_factory, ClearableFileInput
from .models import Product, Review, Category, ProductStock, ContactRequest, Combo, ComboItem, ComboImage, ProductImage

class ProductForm(forms.ModelForm):
    # Size fields for stock management
    size_s_stock = forms.IntegerField(min_value=0, initial=0, label='Size S Stock', required=False)
    size_m_stock = forms.IntegerField(min_value=0, initial=0, label='Size M Stock', required=False)
    size_l_stock = forms.IntegerField(min_value=0, initial=0, label='Size L Stock', required=False)
    size_xl_stock = forms.IntegerField(min_value=0, initial=0, label='Size XL Stock', required=False)
    size_xxl_stock = forms.IntegerField(min_value=0, initial=0, label='Size XXL Stock', required=False)
    
    class Meta:
        model = Product
        fields = ['name', 'slug', 'description', 'price', 'category', 'image', 'hsn_code', 'available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'hsn_code': forms.TextInput(attrs={'placeholder': 'e.g. 6109.10.00'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing existing product, populate size stock fields
        if self.instance and self.instance.pk:
            for stock in self.instance.size_stocks.all():
                field_name = f'size_{stock.size.lower()}_stock'
                if field_name in self.fields:
                    self.fields[field_name].initial = stock.quantity
        
        # Set CSS classes
        for field_name, field in self.fields.items():
            if field_name == 'available':
                field.widget.attrs['class'] = 'form-checkbox'
            elif field_name.endswith('_stock'):
                field.widget.attrs['class'] = 'form-input w-20'
            else:
                field.widget.attrs['class'] = 'form-input'
    
    def save(self, commit=True):
        product = super().save(commit)
        
        if commit:
            # Create or update ProductStock entries
            size_mapping = {
                'size_s_stock': 'S',
                'size_m_stock': 'M', 
                'size_l_stock': 'L',
                'size_xl_stock': 'XL',
                'size_xxl_stock': 'XXL',
            }
            
            for field_name, size_code in size_mapping.items():
                quantity = self.cleaned_data.get(field_name, 0)
                if quantity > 0:  # Only create stock entries for sizes with quantity > 0
                    stock, created = ProductStock.objects.get_or_create(
                        product=product,
                        size=size_code,
                        defaults={'quantity': quantity}
                    )
                    if not created:
                        stock.quantity = quantity
                        stock.save()
                else:
                    # Remove stock entry if quantity is 0
                    ProductStock.objects.filter(product=product, size=size_code).delete()
            
            # Update aggregate stock for legacy compatibility
            product.stock = product.total_stock()
            product.save(update_fields=['stock'])
        
        return product

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'tax_percentage']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'tax_percentage': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '18.00'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ['first_name', 'last_name', 'email', 'subject', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your.email@example.com'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={
                'rows': 5, 
                'placeholder': 'Tell us how we can help you...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set CSS classes for form styling
        for field_name, field in self.fields.items():
            if field_name == 'subject':
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500'
            else:
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500'
        
        # Make all fields required
        for field in self.fields.values():
            field.required = True


class ComboForm(forms.ModelForm):
    class Meta:
        model = Combo
        fields = ['name', 'slug', 'description', 'image', 'price', 'active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'

ComboItemFormSet = inlineformset_factory(
    Combo,
    ComboItem,
    fields=('product', 'quantity'),
    extra=1,
    can_delete=True,
)

ComboImageFormSet = inlineformset_factory(
    Combo,
    ComboImage,
    fields=('image', 'alt_text'),
    extra=1,
    can_delete=True,
)

ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    fields=('image', 'alt_text'),
    extra=1,
    can_delete=True,
    max_num=10,  # Allow up to 10 additional images
    validate_max=True,
)

class MultipleFileInput(forms.ClearableFileInput):
    """
    Custom widget that supports multiple file uploads
    """
    def __init__(self, attrs=None):
        super().__init__(attrs)
        if attrs is None:
            attrs = {}
        attrs['multiple'] = True
        self.attrs.update(attrs)

class MultipleImageUploadForm(forms.Form):
    """
    Enhanced form for multiple image uploads with drag & drop support
    """
    images = forms.FileField(
        widget=MultipleFileInput(attrs={
            'accept': 'image/*',
            'class': 'hidden'
        }),
        required=False,
        help_text='Select multiple images (PNG, JPG, JPEG, GIF, WEBP)'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['images'].widget.attrs.update({
            'id': 'multiple-image-upload',
            'data-max-files': '10',
            'data-max-size': '5242880',  # 5MB in bytes
            'data-allowed-types': 'image/png,image/jpeg,image/jpg,image/gif,image/webp'
        })
    
    def clean_images(self):
        images = self.files.getlist('images')
        
        if not images:
            return images
        
        # Validate number of images
        if len(images) > 10:
            raise forms.ValidationError('You can upload a maximum of 10 images at once.')
        
        # Validate each image
        valid_images = []
        allowed_formats = ['PNG', 'JPG', 'JPEG', 'GIF', 'WEBP']
        max_size = 5 * 1024 * 1024  # 5MB
        
        for image in images:
            # Check file size
            if image.size > max_size:
                raise forms.ValidationError(f'Image "{image.name}" is too large. Maximum size is 5MB.')
            
            # Check file format
            try:
                from PIL import Image
                img = Image.open(image)
                if img.format not in allowed_formats:
                    allowed_formats_str = ', '.join(allowed_formats)
                    raise forms.ValidationError(f'Image "{image.name}" has unsupported format. Allowed: {allowed_formats_str}')
                
                # Reset file pointer
                image.seek(0)
                valid_images.append(image)
            except Exception as e:
                raise forms.ValidationError(f'Image "{image.name}" is not a valid image file.')
        
        return valid_images

class ContactReplyForm(forms.Form):
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500',
            'placeholder': 'Re: Your inquiry about...'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500',
            'rows': 8,
            'placeholder': 'Thank you for contacting us. Here is our response...'
        })
    )
    
    def __init__(self, *args, contact_request=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if contact_request:
            # Pre-fill subject with reference to original inquiry
            original_subject = contact_request.get_subject_display()
            self.fields['subject'].initial = f"Re: {original_subject} - Your inquiry"
            
            # Pre-fill message with a professional template
            customer_name = contact_request.first_name or "Valued Customer"
            self.fields['message'].initial = f"""Dear {customer_name},

Thank you for contacting JOOG Wear. We have received your inquiry regarding "{original_subject}".

[Please provide your response here]

If you have any further questions, please don't hesitate to contact us.

Best regards,
JOOG Wear Customer Service Team

---
Original Message:
"{contact_request.message}"

From: {contact_request.full_name} ({contact_request.email})
Date: {contact_request.created_at.strftime('%B %d, %Y at %I:%M %p')}
"""
