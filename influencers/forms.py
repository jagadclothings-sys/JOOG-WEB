from django import forms
from django.core.exceptions import ValidationError
from .models import Influencer, InfluencerCoupon
from coupons.models import Coupon

class InfluencerLoginForm(forms.Form):
    """Form for influencer login using username and API key"""
    
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your username',
            'required': True
        }),
        help_text="Your unique username provided by the admin"
    )
    
    api_key = forms.CharField(
        max_length=64,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your API key',
            'required': True,
            'type': 'password'
        }),
        help_text="Your secure API key (64 characters)"
    )
    
    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if not username:
            raise forms.ValidationError("Username is required")
        return username
    
    def clean_api_key(self):
        api_key = self.cleaned_data['api_key'].strip()
        if not api_key:
            raise forms.ValidationError("API key is required")
        if len(api_key) != 64:
            raise forms.ValidationError("API key must be exactly 64 characters")
        return api_key


class InfluencerForm(forms.ModelForm):
    """Form for creating and editing influencers in admin"""
    
    class Meta:
        model = Influencer
        fields = [
            'name', 'email', 'username', 'phone', 'commission_rate',
            'instagram_handle', 'youtube_channel', 'tiktok_handle', 'website',
            'notes', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique username'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'commission_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter commission rate (%)',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'instagram_handle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Instagram username (without @)'
            }),
            'youtube_channel': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'YouTube channel name'
            }),
            'tiktok_handle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'TikTok username (without @)'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Internal notes about this influencer',
                'rows': 4
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields required
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['username'].required = True
        
        # Add help text
        self.fields['commission_rate'].help_text = 'Commission percentage (e.g., 5.0 for 5%)'
        self.fields['username'].help_text = 'Unique username for login (cannot be changed after creation)'
        self.fields['is_active'].help_text = 'Whether the influencer can access their dashboard'
    
    def clean_username(self):
        username = self.cleaned_data['username']
        
        # Check if username already exists (excluding current instance)
        existing = Influencer.objects.filter(username=username)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise ValidationError('This username is already taken.')
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        
        # Check if email already exists (excluding current instance)
        existing = Influencer.objects.filter(email=email)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise ValidationError('This email is already registered.')
        
        return email
    
    def clean_commission_rate(self):
        rate = self.cleaned_data['commission_rate']
        
        if rate < 0 or rate > 100:
            raise ValidationError('Commission rate must be between 0 and 100.')
        
        return rate


class InfluencerCouponAssignmentForm(forms.Form):
    """Form for assigning coupons to influencers"""
    
    coupon = forms.ModelChoiceField(
        queryset=Coupon.objects.all(),
        empty_label="Select a coupon to assign",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Optional notes about this assignment',
            'rows': 3
        })
    )
    
    def __init__(self, influencer=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if influencer:
            # Exclude already assigned coupons
            assigned_coupon_ids = influencer.coupons.values_list('coupon_id', flat=True)
            self.fields['coupon'].queryset = Coupon.objects.exclude(
                id__in=assigned_coupon_ids
            ).filter(active=True)
