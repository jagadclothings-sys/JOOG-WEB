from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the signup form.
        """
        from allauth.account.utils import user_username, user_email, user_field
        
        data = form.cleaned_data
        email = data.get('email')
        username = data.get('username')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        user_email(user, email)
        user_username(user, username)
        if first_name:
            user_field(user, 'first_name', first_name)
        if last_name:
            user_field(user, 'last_name', last_name)
        
        if 'password1' in data:
            user.set_password(data['password1'])
        else:
            user.set_unusable_password()
        
        self.populate_username(request, user)
        if commit:
            user.save()
        return user

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a social provider.
        """
        user = sociallogin.user
        if user.id:
            return
        
        if not user.email:
            return
        
        try:
            # Check if a user with this email already exists
            existing_user = User.objects.get(email=user.email)
            # If user exists, connect the social account to the existing user
            sociallogin.connect(request, existing_user)
        except User.DoesNotExist:
            # User doesn't exist, create a new one
            pass

    def populate_user(self, request, sociallogin, data):
        """
        Populates user information from social provider data.
        """
        user = sociallogin.user
        user.email = data.get('email', '')
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        user.username = data.get('email', '')  # Use email as username
        return user
