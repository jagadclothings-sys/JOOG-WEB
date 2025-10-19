from django.core.management.base import BaseCommand, CommandError
from products.models import Category, Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Manage tax rates for categories and products'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Available actions')

        # Set category tax rate
        set_category_parser = subparsers.add_parser('set-category-tax', help='Set tax rate for a category')
        set_category_parser.add_argument('category_name', type=str, help='Category name')
        set_category_parser.add_argument('tax_rate', type=float, help='Tax rate percentage (e.g., 18.0)')

        # Update all products in category
        update_parser = subparsers.add_parser('update-products', help='Update all products in category to match category tax rate')
        update_parser.add_argument('category_name', type=str, help='Category name')

        # List categories with tax rates
        list_parser = subparsers.add_parser('list-categories', help='List all categories with their tax rates')

        # List products with mismatched tax rates
        mismatch_parser = subparsers.add_parser('list-mismatched', help='List products with tax rates different from their category')

        # Sync all products to category rates
        sync_parser = subparsers.add_parser('sync-all', help='Sync all products to their category tax rates')

    def handle(self, *args, **options):
        action = options['action']

        if action == 'set-category-tax':
            self.set_category_tax(options['category_name'], options['tax_rate'])
        elif action == 'update-products':
            self.update_products_in_category(options['category_name'])
        elif action == 'list-categories':
            self.list_categories()
        elif action == 'list-mismatched':
            self.list_mismatched_products()
        elif action == 'sync-all':
            self.sync_all_products()
        else:
            raise CommandError('Invalid action')

    def set_category_tax(self, category_name, tax_rate):
        try:
            category = Category.objects.get(name__iexact=category_name)
        except Category.DoesNotExist:
            raise CommandError(f'Category "{category_name}" not found')

        old_rate = category.tax_percentage
        category.tax_percentage = Decimal(str(tax_rate))
        category.save()  # This will auto-update all products due to our save method

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated category "{category.name}" tax rate from {old_rate}% to {tax_rate}%'
            )
        )
        
        updated_count = category.products.count()
        self.stdout.write(f'Updated {updated_count} products in this category')

    def update_products_in_category(self, category_name):
        try:
            category = Category.objects.get(name__iexact=category_name)
        except Category.DoesNotExist:
            raise CommandError(f'Category "{category_name}" not found')

        updated_count = category.update_products_tax_rate()
        self.stdout.write(
            self.style.SUCCESS(
                f'Updated {updated_count} products in category "{category.name}" to {category.tax_percentage}%'
            )
        )

    def list_categories(self):
        categories = Category.objects.all().order_by('name')
        
        self.stdout.write('\n📊 Category Tax Rates:')
        self.stdout.write('-' * 50)
        
        for category in categories:
            product_count = category.products.count()
            self.stdout.write(
                f'{category.name}: {category.tax_percentage}% ({product_count} products)'
            )

    def list_mismatched_products(self):
        mismatched = []
        
        for product in Product.objects.select_related('category').all():
            if product.category and product.tax_percentage != product.category.tax_percentage:
                mismatched.append(product)
        
        if mismatched:
            self.stdout.write('\n⚠️  Products with different tax rates than their category:')
            self.stdout.write('-' * 60)
            
            for product in mismatched:
                self.stdout.write(
                    f'{product.name} ({product.category.name}): '
                    f'Product: {product.tax_percentage}% | '
                    f'Category: {product.category.tax_percentage}%'
                )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ All products match their category tax rates!')
            )

    def sync_all_products(self):
        total_updated = 0
        
        for category in Category.objects.all():
            updated_count = category.update_products_tax_rate()
            total_updated += updated_count
            
            if updated_count > 0:
                self.stdout.write(f'Updated {updated_count} products in "{category.name}"')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Synced {total_updated} products to their category tax rates')
        )