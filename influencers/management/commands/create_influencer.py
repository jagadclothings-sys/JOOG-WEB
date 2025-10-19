from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from influencers.models import Influencer, InfluencerCoupon
from coupons.models import Coupon
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a new influencer with credentials and optionally assign coupon codes'
    
    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Influencer display name')
        parser.add_argument('email', type=str, help='Influencer email address')
        parser.add_argument('username', type=str, help='Unique username for login')
        
        # Optional arguments
        parser.add_argument('--phone', type=str, help='Phone number', default='')
        parser.add_argument('--instagram', type=str, help='Instagram handle (without @)', default='')
        parser.add_argument('--youtube', type=str, help='YouTube channel name', default='')
        parser.add_argument('--tiktok', type=str, help='TikTok handle (without @)', default='')
        parser.add_argument('--website', type=str, help='Personal website URL', default='')
        parser.add_argument('--commission', type=float, help='Commission rate percentage (e.g., 5.0 for 5 percent)', default=0.0)
        parser.add_argument('--coupon-codes', nargs='+', help='Coupon codes to assign to this influencer', default=[])
        parser.add_argument('--notes', type=str, help='Admin notes about this influencer', default='')
        parser.add_argument('--inactive', action='store_true', help='Create influencer as inactive')
    
    def handle(self, *args, **options):
        try:
            # Create the influencer
            influencer = Influencer(
                name=options['name'],
                email=options['email'],
                username=options['username'],
                phone=options['phone'],
                instagram_handle=options['instagram'],
                youtube_channel=options['youtube'],
                tiktok_handle=options['tiktok'],
                website=options['website'],
                commission_rate=options['commission'],
                notes=options['notes'],
                is_active=not options['inactive']
            )
            
            # Validate and save
            influencer.full_clean()
            influencer.save()
            
            # Assign coupon codes if provided
            assigned_coupons = []
            if options['coupon_codes']:
                admin_user = User.objects.filter(is_staff=True, is_superuser=True).first()
                
                for coupon_code in options['coupon_codes']:
                    try:
                        coupon = Coupon.objects.get(code=coupon_code)
                        influencer_coupon = InfluencerCoupon.objects.create(
                            influencer=influencer,
                            coupon=coupon,
                            assigned_by=admin_user,
                            notes=f'Auto-assigned during influencer creation'
                        )
                        assigned_coupons.append(coupon_code)
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Assigned coupon: {coupon_code}')
                        )
                    except Coupon.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'⚠ Coupon not found: {coupon_code}')
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'✗ Error assigning coupon {coupon_code}: {str(e)}')
                        )
            
            # Display success message with credentials
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('🎉 INFLUENCER CREATED SUCCESSFULLY!'))
            self.stdout.write('='*60)
            
            self.stdout.write(f'Name: {influencer.name}')
            self.stdout.write(f'Email: {influencer.email}')
            self.stdout.write(f'Username: {influencer.username}')
            self.stdout.write(f'Status: {"Active" if influencer.is_active else "Inactive"}')
            self.stdout.write(f'Commission Rate: {influencer.commission_rate}%')
            
            self.stdout.write('\n📱 SOCIAL MEDIA:')
            if influencer.instagram_handle:
                self.stdout.write(f'Instagram: @{influencer.instagram_handle}')
            if influencer.youtube_channel:
                self.stdout.write(f'YouTube: {influencer.youtube_channel}')
            if influencer.tiktok_handle:
                self.stdout.write(f'TikTok: @{influencer.tiktok_handle}')
            if influencer.website:
                self.stdout.write(f'Website: {influencer.website}')
            
            self.stdout.write('\n🔑 LOGIN CREDENTIALS:')
            self.stdout.write(f'Username: {influencer.username}')
            self.stdout.write(f'API Key: {influencer.api_key}')
            
            self.stdout.write('\n🔗 DASHBOARD ACCESS:')
            dashboard_url = f'/influencers/dashboard/?username={influencer.username}&api_key={influencer.api_key}'
            self.stdout.write(f'Dashboard URL: {dashboard_url}')
            
            if assigned_coupons:
                self.stdout.write('\n🎫 ASSIGNED COUPONS:')
                for coupon_code in assigned_coupons:
                    self.stdout.write(f'✓ {coupon_code}')
            
            self.stdout.write('\n📋 NEXT STEPS:')
            self.stdout.write('1. Share the dashboard URL with the influencer')
            self.stdout.write('2. Provide them with their username and API key')
            self.stdout.write('3. Assign additional coupon codes if needed via admin panel')
            self.stdout.write('4. Set up commission tracking and payment schedules')
            
            self.stdout.write('\n' + '='*60)
            
        except ValidationError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Validation Error: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating influencer: {str(e)}')
            )
    
    def get_help_text(self):
        return '''
Create a new influencer with credentials and optionally assign coupon codes.

Examples:
    # Basic influencer creation
    python manage.py create_influencer "John Doe" "john@example.com" "johndoe123"
    
    # Full influencer creation with social media and coupons
    python manage.py create_influencer "Jane Smith" "jane@example.com" "janesmith" \
        --phone "+1234567890" \
        --instagram "janesmith" \
        --youtube "JaneSmithChannel" \
        --commission 5.0 \
        --coupon-codes JANE20 JANE30 \
        --notes "Top fashion influencer with 100K followers"
    
    # Create inactive influencer
    python manage.py create_influencer "Test User" "test@example.com" "testuser" --inactive
        '''