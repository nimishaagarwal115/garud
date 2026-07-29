from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Populates categories using direct SQL to bypass constraint issues.'

    def handle(self, *args, **kwargs):
        categories = [
            # Basic categories for now
            ('Electronics', 'Electronic devices, gadgets, and accessories'),
            ('Fashion & Clothing', 'Clothing, shoes, accessories, and fashion items'),
            ('Home & Garden', 'Home decor, furniture, gardening supplies'),
            ('Health & Beauty', 'Healthcare products, cosmetics, and personal care'),
            ('Sports & Fitness', 'Sports equipment and fitness gear'),
            ('Books & Media', 'Books, magazines, music, and educational materials'),
            ('Toys & Games', 'Toys, board games, video games'),
            ('Food & Beverages', 'Food items and beverages'),
            ('Automotive', 'Car parts and automotive tools'),
            ('Arts & Crafts', 'Art supplies and craft materials'),
            ('Office & Business', 'Office supplies and business equipment'),
            ('Pet Supplies', 'Pet food, toys, and care products'),
            ('Baby & Kids', 'Baby products and children\'s items'),
            ('Travel & Luggage', 'Travel accessories and luggage'),
            ('Music & Instruments', 'Musical instruments and audio equipment'),
        ]

        with connection.cursor() as cursor:
            # Get current timestamp
            cursor.execute("SELECT NOW()")
            now = cursor.fetchone()[0]
            
            for name, description in categories:
                # Check if category exists
                cursor.execute(
                    "SELECT id FROM account_categorymodel WHERE name = %s", 
                    [name]
                )
                if cursor.fetchone():
                    self.stdout.write(self.style.WARNING(f"→ Category '{name}' already exists"))
                    continue
                
                # Insert category with all required fields
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

        # Display summary
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM account_categorymodel")
            total = cursor.fetchone()[0]
            
        self.stdout.write(self.style.SUCCESS(f"\n🎉 Categories setup complete!"))
        self.stdout.write(self.style.SUCCESS(f"📊 Total categories: {total}"))
        self.stdout.write(self.style.SUCCESS(f"\n💡 Now you can use voice commands to select categories in your upload wizard!"))
