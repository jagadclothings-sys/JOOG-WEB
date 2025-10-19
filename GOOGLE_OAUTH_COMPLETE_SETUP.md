# Complete Google OAuth Setup Instructions

Your JOOG e-commerce project now has Google OAuth login functionality fully configured! Here's how to complete the setup:

## ✅ What's Already Done

- ✅ Django-allauth is installed and configured
- ✅ Google OAuth provider is enabled
- ✅ Templates have Google Sign-in buttons
- ✅ URL routing is properly configured
- ✅ Custom social account adapter is set up
- ✅ Management command for setup is ready
- ✅ Environment variable support is configured

## 🔧 What You Need to Do

### Step 1: Get Google OAuth Credentials

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
   - Save and copy your Client ID and Client Secret

### Step 2: Set Up Environment Variables

Create a `.env` file in your project root (copy from `.env.example`):

```bash
# Copy the example file
copy .env.example .env
```

Then edit the `.env` file and update these lines:

```env
GOOGLE_OAUTH2_CLIENT_ID=your_actual_google_client_id
GOOGLE_OAUTH2_CLIENT_SECRET=your_actual_google_client_secret
```

### Step 3: Set Up the Database

Run the setup command with your credentials:

```bash
python manage.py setup_google_oauth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
```

Or if you've set the environment variables in `.env`:

```bash
python manage.py setup_google_oauth
```

### Step 4: Start the Server and Test

```bash
python manage.py runserver
```

Visit `http://localhost:8000/accounts/login/` and test the "Continue with Google" button.

## 🌟 Features Included

- **Login Page**: Google Sign-in button on `/accounts/login/`
- **Registration Page**: Google Sign-in button on `/accounts/register/`
- **Automatic User Creation**: New users are automatically created when signing in with Google
- **Account Linking**: Existing users with the same email are automatically linked
- **Custom User Model**: Fully integrated with your CustomUser model
- **Secure Setup**: Uses environment variables for credentials

## 🔍 Testing the Integration

1. Click "Continue with Google" on the login page
2. You should be redirected to Google's OAuth consent screen
3. After authorization, you should be logged in to your site
4. Check that your user profile is populated with Google account info

## ⚠️ Troubleshooting

### Common Issues:

1. **"Invalid redirect URI" error:**
   - Make sure your redirect URI in Google Console matches exactly: `http://localhost:8000/accounts/google/login/callback/`
   - Check for trailing slashes

2. **"Client ID not found" error:**
   - Verify your Client ID is correct in the `.env` file
   - Run the setup command again with `--force-update`

3. **"Access blocked" error:**
   - Check if your app is in testing mode in Google Console
   - Add test users or publish your app

4. **User not created:**
   - Check the console for error messages
   - Verify email field is properly configured

## 🚀 Production Deployment

When deploying to production:

1. Update your Google OAuth settings with production domain
2. Set up proper environment variables on your server
3. Update the redirect URI to use `https://yourdomain.com/accounts/google/login/callback/`
4. Run the setup command on your production server
5. Test thoroughly before going live

## 📝 Quick Commands Reference

```bash
# Setup Google OAuth with credentials
python manage.py setup_google_oauth --client-id YOUR_ID --client-secret YOUR_SECRET

# Update existing OAuth app
python manage.py setup_google_oauth --client-id NEW_ID --client-secret NEW_SECRET --force-update

# Check system for issues
python manage.py check

# Run development server
python manage.py runserver
```

## 🔐 Security Notes

- Never commit your actual OAuth credentials to version control
- Use environment variables for all sensitive data
- The `.env` file is already in `.gitignore`
- Consider using a secrets management service for production

## 📞 Support

If you encounter any issues:

1. Check Django logs for error messages
2. Check Google Cloud Console for OAuth errors  
3. Check browser developer tools for JavaScript errors
4. Verify network requests in the Network tab

Your Google OAuth login is now ready! Just complete the steps above to start using it.