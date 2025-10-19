# Google OAuth Setup Guide for JOOG E-commerce

This guide will help you set up Google Sign-In functionality for your JOOG e-commerce website.

## Prerequisites

1. A Google Cloud Console account
2. Django project with django-allauth installed

## Step 1: Create Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API"
   - Click on it and press "Enable"

4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - For development: `http://localhost:8000/accounts/google/login/callback/`
     - For production: `https://yourdomain.com/accounts/google/login/callback/`
   - Save and note down your Client ID and Client Secret

## Step 2: Configure Django Settings

Update your `joog_ecommerce/settings.py` with your Google OAuth credentials:

```python
# Google OAuth Settings
GOOGLE_OAUTH2_CLIENT_ID = 'your-actual-client-id'
GOOGLE_OAUTH2_CLIENT_SECRET = 'your-actual-client-secret'
```

## Step 3: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 4: Set Up Google OAuth Provider

Run the setup command:

```bash
python manage.py setup_google_oauth
```

## Step 5: Update OAuth Credentials in Admin

1. Go to your Django admin panel
2. Navigate to "Social Applications"
3. Find the Google app and update it with your actual credentials:
   - Client ID: Your Google OAuth Client ID
   - Secret Key: Your Google OAuth Client Secret

## Step 6: Test the Integration

1. Start your Django server: `python manage.py runserver`
2. Go to the login page: `http://localhost:8000/accounts/login/`
3. Click "Continue with Google"
4. You should be redirected to Google's OAuth consent screen
5. After authorization, you should be logged in to your site

## Features Included

- ✅ Google Sign-In button on login page
- ✅ Google Sign-In button on registration page
- ✅ Automatic user creation for new Google users
- ✅ Account linking for existing users with same email
- ✅ Custom user model integration
- ✅ Proper error handling

## Troubleshooting

### Common Issues:

1. **"Invalid redirect URI" error:**
   - Make sure your redirect URI in Google Console matches exactly
   - Check for trailing slashes and http vs https

2. **"Client ID not found" error:**
   - Verify your Client ID is correct in the admin panel
   - Make sure the Google app is associated with the correct site

3. **"Access blocked" error:**
   - Check if your app is in testing mode in Google Console
   - Add test users or publish your app

4. **User not created:**
   - Check the CustomSocialAccountAdapter in accounts/adapters.py
   - Verify email field is properly configured

## Security Notes

- Never commit your actual OAuth credentials to version control
- Use environment variables for production:
  ```python
  import os
  GOOGLE_OAUTH2_CLIENT_ID = os.getenv('GOOGLE_OAUTH2_CLIENT_ID')
  GOOGLE_OAUTH2_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET')
  ```

## Production Deployment

1. Update your Google OAuth settings with production domain
2. Set up proper environment variables
3. Update the site domain in Django admin
4. Test thoroughly before going live

## Support

If you encounter any issues, check:
1. Django logs for error messages
2. Google Cloud Console for OAuth errors
3. Browser developer tools for JavaScript errors
4. Network tab for failed requests
