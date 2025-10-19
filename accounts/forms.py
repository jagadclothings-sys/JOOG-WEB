from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.validators import RegexValidator
from .models import CustomUser, Address
import json as _json
from urllib.request import urlopen as _urlopen
from urllib.error import URLError as _URLError
import re as _re

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        validators=[
            RegexValidator(
                regex=r"^\+?[1-9]\d{6,14}$",
                message="Enter a valid international phone number (E.164).",
            )
        ],
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'phone_number':
                field.widget.attrs['class'] = 'form-input numeric-font'
            else:
                field.widget.attrs['class'] = 'form-input'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'address', 'city', 'state', 'postal_code', 'country')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'phone_number':
                field.widget.attrs['class'] = 'form-input numeric-font'
            else:
                field.widget.attrs['class'] = 'form-input'
            if field_name == 'email':
                field.required = True
            elif field_name in ['phone_number', 'address', 'city', 'state', 'postal_code', 'country']:
                field.required = False
                
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def clean_postal_code(self):
        code = (self.cleaned_data.get('postal_code') or '').strip()
        if not code:
            return code
        if not _re.match(r'^\d{6}$', code):
            raise forms.ValidationError('Enter a valid 6-digit PIN code.')
        # Validate against India Postal API
        try:
            with _urlopen(f'https://api.postalpincode.in/pincode/{code}', timeout=5) as resp:
                data = _json.loads(resp.read().decode('utf-8'))
            if not data or data[0].get('Status') != 'Success' or not data[0].get('PostOffice'):
                raise forms.ValidationError('Enter a valid Indian PIN code.')
            post_office = data[0]['PostOffice'][0]
            self._pin_city = post_office.get('District') or post_office.get('Region')
            self._pin_state = post_office.get('State')
            self._pin_country = post_office.get('Country') or 'India'
        except _URLError:
            # Network issue: silently skip API verification
            pass
        return code

    def clean(self):
        cleaned = super().clean()
        if getattr(self, '_pin_city', None) and not (cleaned.get('city') or '').strip():
            cleaned['city'] = self._pin_city
        if getattr(self, '_pin_state', None) and not (cleaned.get('state') or '').strip():
            cleaned['state'] = self._pin_state
        if getattr(self, '_pin_country', None) and not (cleaned.get('country') or '').strip():
            cleaned['country'] = self._pin_country
        return cleaned

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_type', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country', 'is_default']
        widgets = {
            'address_line_1': forms.TextInput(attrs={'placeholder': 'Street address, building, apartment'}),
            'address_line_2': forms.TextInput(attrs={'placeholder': 'Apartment, suite, unit, etc. (optional)'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State/Province'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'PIN Code'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'postal_code':
                field.widget.attrs['class'] = 'form-input numeric-font'
            else:
                field.widget.attrs['class'] = 'form-input'
                
            if field_name == 'address_line_2':
                field.required = False
            elif field_name == 'is_default':
                field.widget.attrs['class'] = 'form-checkbox'
                field.required = False
    
    def clean_postal_code(self):
        code = (self.cleaned_data.get('postal_code') or '').strip()
        if not code:
            raise forms.ValidationError('PIN code is required.')
        if not _re.match(r'^\d{6}$', code):
            raise forms.ValidationError('Enter a valid 6-digit PIN code.')
        
        # Validate against India Postal API
        try:
            with _urlopen(f'https://api.postalpincode.in/pincode/{code}', timeout=5) as resp:
                data = _json.loads(resp.read().decode('utf-8'))
            if not data or data[0].get('Status') != 'Success' or not data[0].get('PostOffice'):
                raise forms.ValidationError('Enter a valid Indian PIN code.')
            
            # Store suggestions for use in clean()
            post_office = data[0]['PostOffice'][0]
            self._pin_city = post_office.get('District') or post_office.get('Region')
            self._pin_state = post_office.get('State')
            self._pin_country = post_office.get('Country') or 'India'
        except _URLError:
            # Network issue: fall back to format-only validation
            pass
        return code
    
    def clean(self):
        cleaned = super().clean()
        # Auto-suggest city/state/country from PIN if fields are empty
        city = (cleaned.get('city') or '').strip()
        state = (cleaned.get('state') or '').strip()
        country = (cleaned.get('country') or '').strip()
        
        if getattr(self, '_pin_city', None) and not city:
            cleaned['city'] = self._pin_city
        if getattr(self, '_pin_state', None) and not state:
            cleaned['state'] = self._pin_state
        if getattr(self, '_pin_country', None) and not country:
            cleaned['country'] = self._pin_country
        
        return cleaned
