from django.core.management.base import BaseCommand
from django.conf import settings
from invoices.models import TaxInvoice

class Command(BaseCommand):
    help = 'Update GSTIN for existing invoices'

    def add_arguments(self, parser):
        parser.add_argument(
            '--gstin',
            type=str,
            help='The actual GSTIN number to update',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        gstin = options.get('gstin')
        dry_run = options.get('dry_run', False)
        
        if not gstin:
            gstin = getattr(settings, 'COMPANY_GSTIN', '')
            if not gstin:
                self.stdout.write(
                    self.style.ERROR(
                        'GSTIN not provided and not found in settings. '
                        'Please provide --gstin argument or set COMPANY_GSTIN in your .env file'
                    )
                )
                return

        # Get all invoices
        invoices = TaxInvoice.objects.all()
        total_invoices = invoices.count()

        if total_invoices == 0:
            self.stdout.write(self.style.WARNING('No invoices found to update.'))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Found {total_invoices} invoice(s) to update with GSTIN: {gstin}'
            )
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    'DRY RUN MODE - No changes will be made. '
                    'Remove --dry-run to apply changes.'
                )
            )
            for invoice in invoices:
                self.stdout.write(
                    f'Would update invoice {invoice.invoice_number}: '
                    f'{invoice.company_gstin} -> {gstin}'
                )
        else:
            updated_count = 0
            for invoice in invoices:
                old_gstin = invoice.company_gstin
                invoice.company_gstin = gstin
                # Also update other company details from settings
                invoice.populate_company_details()
                invoice.save()
                updated_count += 1
                
                self.stdout.write(
                    f'Updated invoice {invoice.invoice_number}: '
                    f'{old_gstin} -> {gstin}'
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} invoice(s) with new GSTIN.'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                '\nRemember to:'
                '\n1. Update your .env file with the actual GSTIN number'
                '\n2. Restart your Django application'
                '\n3. All new invoices will automatically use the new GSTIN'
            )
        )