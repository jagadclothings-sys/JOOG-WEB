#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'joog_ecommerce.settings')
django.setup()

from influencers.models import Influencer

print("=" * 60)
print("🔑 INFLUENCER LOGIN CREDENTIALS")
print("=" * 60)

influencers = Influencer.objects.filter(is_active=True)

if not influencers:
    print("❌ No active influencers found!")
    print("\n💡 Create one using:")
    print('python manage.py create_influencer "Name" "email@example.com" "username"')
else:
    for i, influencer in enumerate(influencers, 1):
        print(f"\n🎯 INFLUENCER #{i}")
        print(f"📛 Username: {influencer.username}")
        print(f"👤 Name: {influencer.name}")
        print(f"📧 Email: {influencer.email}")
        print(f"🔑 API Key: {influencer.api_key}")
        print(f"💰 Commission: {influencer.commission_rate}%")
        
        # Show assigned coupons
        coupon_count = influencer.coupons.count()
        if coupon_count > 0:
            coupons = [ic.coupon.code for ic in influencer.coupons.all()[:3]]
            print(f"🎫 Coupons: {', '.join(coupons)} ({coupon_count} total)")
        else:
            print("🎫 Coupons: None assigned")
        
        # Direct login URLs
        print(f"\n🔗 DIRECT LOGIN LINKS:")
        print(f"   Manual Login: http://127.0.0.1:8000/influencers/login/")
        print(f"   Auto Login:   http://127.0.0.1:8000/influencers/login/?username={influencer.username}&api_key={influencer.api_key}")
        print("-" * 60)

print(f"\n✅ Total Active Influencers: {influencers.count()}")
print("\n📋 MANUAL LOGIN INSTRUCTIONS:")
print("1. Go to: http://127.0.0.1:8000/influencers/login/")
print("2. Enter the Username and API Key from above")
print("3. Click Login to access dashboard")

print("\n🚀 OR USE DIRECT LINKS:")
print("Click the 'Auto Login' links above for instant access!")
print("=" * 60)