from django.core.management.base import BaseCommand
from account.models import CategoryModel

class Command(BaseCommand):
    help = 'List all categories with their details.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='Show only active categories',
        )
        parser.add_argument(
            '--add',
            type=str,
            help='Add a new category with given name',
        )
        parser.add_argument(
            '--description',
            type=str,
            help='Description for the new category (use with --add)',
        )

    def handle(self, *args, **options):
        if options['add']:
            name = options['add']
            description = options.get('description', f'{name} products and related items')
            
            # Create category using SQL to avoid constraint issues
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT NOW()")
                now = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO account_categorymodel 
                    (created_at, updated_at, create_by, update_by, name, description, 
                     image, is_active, parent_id, name_detected_script, name_devanagari, 
                     name_original, name_roman, name_search_variants, 
                     description_detected_script, description_devanagari, 
                     description_original, description_roman, description_search_variants)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    now, now, None, None, name, description, 
                    '', True, None, '', '', '', '', '', '', '', '', '', ''
                ])
                
            self.stdout.write(self.style.SUCCESS(f"✓ Added category: {name}"))
            return

        # List categories
        if options['active_only']:
            categories = CategoryModel.objects.filter(is_active=True).order_by('name')
            self.stdout.write(self.style.SUCCESS("📁 Active Categories:"))
        else:
            categories = CategoryModel.objects.all().order_by('name')
            self.stdout.write(self.style.SUCCESS("📁 All Categories:"))
        
        if not categories:
            self.stdout.write(self.style.WARNING("No categories found."))
            return
        
        self.stdout.write("-" * 80)
        
        for category in categories:
            status = "✅ Active" if category.is_active else "❌ Inactive"
            parent_info = f" (Parent: {category.parent.name})" if category.parent else ""
            
            self.stdout.write(f"📂 {category.name}{parent_info}")
            self.stdout.write(f"   {status} | ID: {category.id}")
            if category.description:
                desc = category.description[:100] + "..." if len(category.description) > 100 else category.description
                self.stdout.write(f"   📝 {desc}")
            self.stdout.write("-" * 80)
        
        total = categories.count()
        if options['active_only']:
            inactive_count = CategoryModel.objects.filter(is_active=False).count()
            self.stdout.write(self.style.SUCCESS(f"\n📊 {total} active categories ({inactive_count} inactive)"))
        else:
            active_count = CategoryModel.objects.filter(is_active=True).count()
            self.stdout.write(self.style.SUCCESS(f"\n📊 {total} total categories ({active_count} active)"))
        
        self.stdout.write(self.style.SUCCESS("\n💡 Usage examples:"))
        self.stdout.write("  python manage.py list_categories --active-only")
        self.stdout.write("  python manage.py list_categories --add 'Smart Devices' --description 'IoT and smart home devices'")
