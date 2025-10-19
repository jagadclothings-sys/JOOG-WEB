from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import logging

from orders.models import Order
from orders.email_utils import EmailService

logger = logging.getLogger('orders.email_utils')

class Command(BaseCommand):
    help = 'Send order confirmation emails for orders that haven\'t been sent yet'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of emails to send (default: 50)',
        )
        
        parser.add_argument(
            '--order-id',
            type=int,
            help='Send confirmation email for specific order ID',
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Dry run - show what would be sent without actually sending',
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force send emails even if already sent',
        )
        
        parser.add_argument(
            '--max-age-hours',
            type=int,
            default=168,  # 7 days
            help='Maximum age of orders to process in hours (default: 168 = 7 days)',
        )
    
    def handle(self, *args, **options):
        email_service = EmailService()
        
        # Statistics
        stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        try:
            # Handle specific order
            if options['order_id']:
                try:
                    order = Order.objects.get(id=options['order_id'])
                    self._process_single_order(order, email_service, options, stats)
                except Order.DoesNotExist:
                    raise CommandError(f'Order with ID {options["order_id"]} does not exist.')
            else:
                # Handle bulk processing
                self._process_bulk_orders(email_service, options, stats)
            
            # Display results
            self._display_results(stats, options['dry_run'])
            
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            raise CommandError(f"Command failed: {str(e)}")
    
    def _process_single_order(self, order, email_service, options, stats):
        """Process a single order"""
        stats['total_processed'] = 1
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would send confirmation email for order {order.order_number}')
            )
            stats['successful'] = 1
            return
        
        success, message = email_service.send_order_confirmation_email_new(order)
        
        if success:
            stats['successful'] = 1
            self.stdout.write(
                self.style.SUCCESS(f'✓ Sent confirmation email for order {order.order_number}')
            )
        else:
            stats['failed'] = 1
            stats['errors'].append(f"Order {order.order_number}: {message}")
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send email for order {order.order_number}: {message}')
            )
    
    def _process_bulk_orders(self, email_service, options, stats):
        """Process orders in bulk"""
        # Build query
        query = Q()
        
        # Age filter
        cutoff_date = timezone.now() - timedelta(hours=options['max_age_hours'])
        query &= Q(created_at__gte=cutoff_date)
        
        # Only process orders that need confirmation emails
        if not options['force']:
            query &= Q(confirmation_email_sent=False)
        
        # Get orders
        orders = Order.objects.filter(query).select_related('user')[:options['limit']]
        
        if not orders:
            self.stdout.write(self.style.SUCCESS('No orders found that need confirmation emails.'))
            return
        
        self.stdout.write(f'Processing {orders.count()} orders...')
        
        for order in orders:
            stats['total_processed'] += 1
            
            # Skip if already sent and not forcing
            if order.confirmation_email_sent and not options['force']:
                stats['skipped'] += 1
                continue
            
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING(f'DRY RUN: Would send confirmation email for order {order.order_number}')
                )
                stats['successful'] += 1
                continue
            
            # Send email
            success, message = email_service.send_order_confirmation_email_new(order)
            
            if success:
                stats['successful'] += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Order {order.order_number}')
                )
            else:
                stats['failed'] += 1
                stats['errors'].append(f"Order {order.order_number}: {message}")
                self.stdout.write(
                    self.style.ERROR(f'✗ Order {order.order_number}: {message}')
                )
    
    def _display_results(self, stats, is_dry_run):
        """Display command results"""
        self.stdout.write('\n' + '='*50)
        
        if is_dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN RESULTS:'))
        else:
            self.stdout.write(self.style.SUCCESS('EXECUTION RESULTS:'))
        
        self.stdout.write(f'Total Processed: {stats["total_processed"]}')
        self.stdout.write(f'Successful: {stats["successful"]}')
        self.stdout.write(f'Failed: {stats["failed"]}')
        self.stdout.write(f'Skipped: {stats["skipped"]}')
        
        if stats['errors']:
            self.stdout.write('\nErrors:')
            for error in stats['errors'][:10]:  # Show first 10 errors
                self.stdout.write(self.style.ERROR(f'  - {error}'))
            
            if len(stats['errors']) > 10:
                self.stdout.write(f'  ... and {len(stats["errors"]) - 10} more errors')
        
        self.stdout.write('='*50)