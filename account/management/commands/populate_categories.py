from django.core.management.base import BaseCommand
from catalogue.models import CategoryModel

class Command(BaseCommand):
    help = 'Populates the CategoryModel with comprehensive default categories.'

    def handle(self, *args, **kwargs):
        categories = [
            # Main Categories
            {'name': 'Electronics', 'description': 'Electronic devices, gadgets, and accessories'},
            {'name': 'Fashion & Clothing', 'description': 'Clothing, shoes, accessories, and fashion items'},
            {'name': 'Home & Garden', 'description': 'Home decor, furniture, gardening supplies, and household items'},
            {'name': 'Health & Beauty', 'description': 'Healthcare products, cosmetics, and personal care items'},
            {'name': 'Sports & Fitness', 'description': 'Sports equipment, fitness gear, and outdoor activities'},
            {'name': 'Books & Media', 'description': 'Books, magazines, music, movies, and educational materials'},
            {'name': 'Toys & Games', 'description': 'Toys, board games, video games, and entertainment'},
            {'name': 'Food & Beverages', 'description': 'Food items, beverages, and grocery products'},
            {'name': 'Automotive', 'description': 'Car parts, accessories, and automotive tools'},
            {'name': 'Arts & Crafts', 'description': 'Art supplies, craft materials, and creative tools'},
            {'name': 'Office & Business', 'description': 'Office supplies, business equipment, and stationery'},
            {'name': 'Pet Supplies', 'description': 'Pet food, toys, accessories, and care products'},
            {'name': 'Baby & Kids', 'description': 'Baby products, children\'s items, and parenting essentials'},
            {'name': 'Travel & Luggage', 'description': 'Travel accessories, luggage, and vacation essentials'},
            {'name': 'Music & Instruments', 'description': 'Musical instruments, audio equipment, and music accessories'},
            
            # Electronics Subcategories
            {'name': 'Mobile Phones', 'description': 'Smartphones, feature phones, and mobile accessories', 'parent_name': 'Electronics'},
            {'name': 'Laptops & Computers', 'description': 'Laptops, desktops, tablets, and computer accessories', 'parent_name': 'Electronics'},
            {'name': 'Audio & Video', 'description': 'Headphones, speakers, cameras, and entertainment devices', 'parent_name': 'Electronics'},
            {'name': 'Gaming', 'description': 'Gaming consoles, video games, and gaming accessories', 'parent_name': 'Electronics'},
            {'name': 'Smart Home', 'description': 'IoT devices, smart speakers, and home automation', 'parent_name': 'Electronics'},
            
            # Fashion Subcategories
            {'name': 'Men\'s Clothing', 'description': 'Shirts, pants, suits, and men\'s fashion', 'parent_name': 'Fashion & Clothing'},
            {'name': 'Women\'s Clothing', 'description': 'Dresses, tops, bottoms, and women\'s fashion', 'parent_name': 'Fashion & Clothing'},
            {'name': 'Shoes & Footwear', 'description': 'Sneakers, boots, sandals, and all types of footwear', 'parent_name': 'Fashion & Clothing'},
            {'name': 'Accessories', 'description': 'Jewelry, watches, bags, and fashion accessories', 'parent_name': 'Fashion & Clothing'},
            {'name': 'Kids\' Clothing', 'description': 'Children\'s clothing and accessories', 'parent_name': 'Fashion & Clothing'},
            
            # Home & Garden Subcategories
            {'name': 'Furniture', 'description': 'Chairs, tables, beds, and home furniture', 'parent_name': 'Home & Garden'},
            {'name': 'Kitchen & Dining', 'description': 'Cookware, appliances, and dining essentials', 'parent_name': 'Home & Garden'},
            {'name': 'Home Decor', 'description': 'Wall art, decorative items, and home styling', 'parent_name': 'Home & Garden'},
            {'name': 'Gardening', 'description': 'Plants, tools, and gardening supplies', 'parent_name': 'Home & Garden'},
            {'name': 'Storage & Organization', 'description': 'Storage solutions and organizational tools', 'parent_name': 'Home & Garden'},
            
            # Health & Beauty Subcategories
            {'name': 'Skincare', 'description': 'Face care, body care, and skin treatments', 'parent_name': 'Health & Beauty'},
            {'name': 'Makeup & Cosmetics', 'description': 'Makeup, nail care, and beauty products', 'parent_name': 'Health & Beauty'},
            {'name': 'Personal Care', 'description': 'Hygiene products, grooming, and personal wellness', 'parent_name': 'Health & Beauty'},
            {'name': 'Health Supplements', 'description': 'Vitamins, supplements, and health products', 'parent_name': 'Health & Beauty'},
            {'name': 'Hair Care', 'description': 'Shampoo, styling products, and hair treatments', 'parent_name': 'Health & Beauty'},
            
            # Sports & Fitness Subcategories
            {'name': 'Exercise Equipment', 'description': 'Gym equipment, weights, and fitness machines', 'parent_name': 'Sports & Fitness'},
            {'name': 'Outdoor Sports', 'description': 'Camping, hiking, and outdoor activity gear', 'parent_name': 'Sports & Fitness'},
            {'name': 'Team Sports', 'description': 'Football, basketball, cricket, and team sport equipment', 'parent_name': 'Sports & Fitness'},
            {'name': 'Water Sports', 'description': 'Swimming, surfing, and water activity equipment', 'parent_name': 'Sports & Fitness'},
            {'name': 'Yoga & Meditation', 'description': 'Yoga mats, meditation accessories, and wellness gear', 'parent_name': 'Sports & Fitness'},
            
            # Additional Popular Categories
            {'name': 'Handmade & Crafts', 'description': 'Handcrafted items, artisan products, and unique creations'},
            {'name': 'Vintage & Antiques', 'description': 'Vintage items, antiques, and collectibles'},
            {'name': 'Digital Products', 'description': 'Software, digital downloads, and online services'},
            {'name': 'Subscription Services', 'description': 'Monthly boxes, memberships, and recurring services'},
            {'name': 'Gift Cards & Vouchers', 'description': 'Gift cards, vouchers, and digital credits'},
        ]

        # First pass: Create main categories
        created_categories = {}
        for category_data in categories:
            if 'parent_name' not in category_data:
                obj, created = CategoryModel.objects.get_or_create(
                    name=category_data['name'],
                    defaults={'description': category_data['description']}
                )
                created_categories[category_data['name']] = obj
                if created:
                    self.stdout.write(self.style.SUCCESS(f"✓ Added main category: {category_data['name']}"))
                else:
                    self.stdout.write(self.style.WARNING(f"→ Main category already exists: {category_data['name']}"))

        # Second pass: Create subcategories with parent relationships
        for category_data in categories:
            if 'parent_name' in category_data:
                parent_name = category_data['parent_name']
                if parent_name in created_categories:
                    parent_category = created_categories[parent_name]
                    obj, created = CategoryModel.objects.get_or_create(
                        name=category_data['name'],
                        defaults={
                            'description': category_data['description'],
                            'parent': parent_category
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"  ✓ Added subcategory: {category_data['name']} under {parent_name}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"  → Subcategory already exists: {category_data['name']}"))
                else:
                    self.stdout.write(self.style.ERROR(f"✗ Parent category '{parent_name}' not found for '{category_data['name']}'"))

        # Display summary
        total_categories = CategoryModel.objects.count()
        main_categories = CategoryModel.objects.filter(parent__isnull=True).count()
        subcategories = CategoryModel.objects.filter(parent__isnull=False).count()
        
        self.stdout.write(self.style.SUCCESS(f"\n🎉 Categories populated successfully!"))
        self.stdout.write(self.style.SUCCESS(f"📊 Total categories: {total_categories}"))
        self.stdout.write(self.style.SUCCESS(f"📁 Main categories: {main_categories}"))
        self.stdout.write(self.style.SUCCESS(f"📂 Subcategories: {subcategories}"))
        self.stdout.write(self.style.SUCCESS(f"\n💡 Run: python manage.py runserver and visit your product upload wizard!"))
