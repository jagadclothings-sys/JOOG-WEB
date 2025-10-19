#!/usr/bin/env python
"""
Google OAuth Setup Script for JOOG E-commerce
Run this script to set up Google OAuth functionality
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'joog_ecommerce.settings')
django.setup()

from django.core.management import call_command
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def setup_google_oauth():
    print("🚀 Setting up Google OAuth for JOOG E-commerce...")
    print("=" * 50)
    
    try:
        # Run migrations
        print("📦 Running database migrations...")
        call_command('makemigrations')
        call_command('migrate')
        print("✅ Migrations completed successfully!")
        
        # Set up site
        print("\n🌐 Setting up site...")
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': 'localhost:8000',
                'name': 'JOOG E-commerce'
            }
        )
        
        if created:
            print(f"✅ Created site: {site.domain}")
        else:
            print(f"✅ Using existing site: {site.domain}")
        
        # Create Google OAuth app
        print("\n🔐 Setting up Google OAuth app...")
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': 'your-google-client-id',
                'secret': 'your-google-client-secret',
            }
        )
        
        if created:
            print("✅ Created Google OAuth app")
        else:
            print("✅ Google OAuth app already exists")
        
        # Add site to the app
        google_app.sites.add(site)
        
        print("\n" + "=" * 50)
        print("🎉 Google OAuth setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Go to Google Cloud Console and create OAuth credentials")
        print("2. Update the Client ID and Secret in Django admin")
        print("3. Test the Google sign-in functionality")
        print("\n📖 For detailed instructions, see GOOGLE_OAUTH_SETUP.md")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        print("Please check your Django configuration and try again.")

if __name__ == "__main__":
    setup_google_oauth()
