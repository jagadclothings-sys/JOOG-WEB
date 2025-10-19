from django import forms
from .models import Order
from accounts.models import Address
import re
import json as _json
from urllib.request import urlopen as _urlopen
from urllib.error import URLError as _URLError

class OrderForm(forms.ModelForm):
    selected_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        empty_label="Select an address",
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    
    class Meta:
        model = Order
        fields = ['selected_address', 'shipping_address', 'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['selected_address'].queryset = Address.objects.filter(user=user)
            
        for field_name, field in self.fields.items():
            if field_name == 'selected_address':
                field.widget.attrs['class'] = 'form-select'
                field.widget.attrs['onchange'] = 'fillAddressFromSelection()'
            else:
                field.widget.attrs['class'] = 'form-input'
                if field_name != 'selected_address':
                    field.required = True
                    
            if field_name == 'shipping_address':
                field.widget.attrs['rows'] = 3
                field.widget.attrs['style'] = 'resize:vertical;'
                field.widget.attrs['placeholder'] = 'Street address, building, apartment'

    def clean_shipping_postal_code(self):
        code = (self.cleaned_data.get('shipping_postal_code') or '').strip()
        if not re.match(r'^\d{6}$', code):
            raise forms.ValidationError('Enter a valid 6-digit PIN code.')
        # Validate against India Postal API
        try:
            with _urlopen(f'https://api.postalpincode.in/pincode/{code}', timeout=5) as resp:
                data = _json.loads(resp.read().decode('utf-8'))
            if not data or data[0].get('Status') != 'Success' or not data[0].get('PostOffice'):
                raise forms.ValidationError('Enter a valid Indian PIN code.')
            # Optionally auto-suggest city/country into cleaned_data if not provided
            post_office = data[0]['PostOffice'][0]
            inferred_city = post_office.get('District') or post_office.get('Region')
            inferred_state = post_office.get('State')
            inferred_country = post_office.get('Country') or 'India'
            # Store suggestions for use in clean()
            self._pin_city = inferred_city
            self._pin_state = inferred_state
            self._pin_country = inferred_country
        except _URLError:
            # Network issue: fall back to format-only validation
            pass
        return code

    def clean(self):
        cleaned = super().clean()
        # If API provided suggestions, use them when fields are empty
        city = (cleaned.get('shipping_city') or '').strip()
        state = (cleaned.get('shipping_state') or '').strip()
        country = (cleaned.get('shipping_country') or '').strip()
        if getattr(self, '_pin_city', None) and not city:
            cleaned['shipping_city'] = self._pin_city
        if getattr(self, '_pin_state', None) and not state:
            cleaned['shipping_state'] = self._pin_state
        if getattr(self, '_pin_country', None) and not country:
            cleaned['shipping_country'] = self._pin_country
        return cleaned