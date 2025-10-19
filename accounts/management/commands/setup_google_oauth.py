from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider


class Command(BaseCommand):
    help = 'Set up Google OAuth for django-allauth'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=str,
            help='Google OAuth Client ID',
        )
        parser.add_argument(
            '--client-secret',
            type=str,
            help='Google OAuth Client Secret',
        )
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Update existing Google OAuth app if it exists',
        )

    def handle(self, *args, **options):
        # Get client ID and secret from arguments or settings
        client_id = options.get('client_id') or settings.GOOGLE_OAUTH2_CLIENT_ID
        client_secret = options.get('client_secret') or settings.GOOGLE_OAUTH2_CLIENT_SECRET

        if client_id == 'your-google-client-id' or client_secret == 'your-google-client-secret':
            self.stdout.write(
                self.style.ERROR(
                    'Please set your Google OAuth credentials in settings or use --client-id and --client-secret arguments'
                )
            )
            return

        # Get the current site
        try:
            site = Site.objects.get(pk=settings.SITE_ID)
        except Site.DoesNotExist:
            site = Site.objects.create(
                pk=settings.SITE_ID,
                domain='localhost:8000',
                name='JOOG E-commerce (Development)'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created site: {site.domain}')
            )

        # Check if Google OAuth app already exists
        try:
            google_app = SocialApp.objects.get(provider=GoogleProvider.id)
            if options.get('force_update'):
                google_app.client_id = client_id
                google_app.secret = client_secret
                google_app.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated existing Google OAuth app with new credentials'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Google OAuth app already exists. Use --force-update to update credentials.'
                    )
                )
                return
        except SocialApp.DoesNotExist:
            # Create new Google OAuth app
            google_app = SocialApp.objects.create(
                provider=GoogleProvider.id,
                name='Google',
                client_id=client_id,
                secret=client_secret,
            )
            self.stdout.write(
                self.style.SUCCESS('Created Google OAuth app')
            )

        # Associate the app with the current site
        google_app.sites.add(site)
        google_app.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Google OAuth setup complete!\n'
                f'Client ID: {client_id[:10]}...\n'
                f'Site: {site.domain}\n'
                f'Make sure to add the following redirect URI in your Google Console:\n'
                f'http://{site.domain}/accounts/google/login/callback/\n'
                f'For production, use https instead of http.'
            )
        )
