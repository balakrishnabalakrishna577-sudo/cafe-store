from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from cafe.models import Category, MenuItem, UserProfile
import os


class Command(BaseCommand):
    help = 'Setup admin user and initial data for the cafe delivery system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@cafedelivery.com',
            help='Admin email (default: admin@cafedelivery.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Admin password (default: admin123)'
        )
        parser.add_argument(
            '--skip-data',
            action='store_true',
            help='Skip creating sample data'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        skip_data = options['skip_data']

        self.stdout.write(
            self.style.SUCCESS('🍕 Setting up Cafe Delivery Admin System...\n')
        )

        try:
            with transaction.atomic():
                # Create or update admin user
                admin_user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'is_staff': True,
                        'is_superuser': True,
                        'first_name': 'Admin',
                        'last_name': 'User'
                    }
                )
                
                if created:
                    admin_user.set_password(password)
                    admin_user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Created admin user: {username}')
                    )
                else:
                    # Update existing user
                    admin_user.email = email
                    admin_user.is_staff = True
                    admin_user.is_superuser = True
                    admin_user.set_password(password)
                    admin_user.save()
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Updated existing admin user: {username}')
                    )

                # Create admin profile
                profile, created = UserProfile.objects.get_or_create(
                    user=admin_user,
                    defaults={
                        'phone': '+91 98765 43210',
                        'address': 'Admin Office, Cafe Delivery HQ',
                        'city': 'Mumbai',
                        'postal_code': '400001'
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Created admin profile')
                    )

                if not skip_data:
                    self.create_sample_data()

                self.stdout.write(
                    self.style.SUCCESS('\n🎉 Admin setup completed successfully!')
                )
                self.stdout.write(
                    self.style.SUCCESS('📋 Admin Panel Details:')
                )
                self.stdout.write(f'   🌐 URL: http://127.0.0.1:8000/admin/')
                self.stdout.write(f'   👤 Username: {username}')
                self.stdout.write(f'   🔑 Password: {password}')
                self.stdout.write(f'   📧 Email: {email}')
                
                self.stdout.write(
                    self.style.SUCCESS('\n🚀 Custom Admin Features:')
                )
                self.stdout.write('   📊 Dashboard Statistics')
                self.stdout.write('   📈 Sales Reports')
                self.stdout.write('   📊 Menu Analytics')
                self.stdout.write('   🛒 Order Management')
                self.stdout.write('   🍕 Menu Management')
                self.stdout.write('   👥 Customer Management')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error setting up admin: {str(e)}')
            )
            raise

    def create_sample_data(self):
        """Create sample categories and menu items if they don't exist"""
        self.stdout.write('📦 Creating sample data...')
        
        # Sample categories
        categories_data = [
            {'name': 'Appetizers', 'description': 'Start your meal with our delicious appetizers'},
            {'name': 'Main Course', 'description': 'Hearty main dishes to satisfy your hunger'},
            {'name': 'Desserts', 'description': 'Sweet treats to end your meal perfectly'},
            {'name': 'Beverages', 'description': 'Refreshing drinks and hot beverages'},
            {'name': 'Snacks', 'description': 'Quick bites and light snacks'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': cat_data['name'].lower().replace(' ', '-'),
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(f'   ✅ Created category: {category.name}')

        # Sample menu items
        if Category.objects.exists():
            appetizer_cat = Category.objects.get(name='Appetizers')
            main_cat = Category.objects.get(name='Main Course')
            dessert_cat = Category.objects.get(name='Desserts')
            beverage_cat = Category.objects.get(name='Beverages')
            
            sample_items = [
                {
                    'name': 'Chicken Wings',
                    'category': appetizer_cat,
                    'price': 299.00,
                    'description': 'Crispy chicken wings with spicy sauce',
                    'discount': 10,
                    'is_featured': True
                },
                {
                    'name': 'Margherita Pizza',
                    'category': main_cat,
                    'price': 399.00,
                    'description': 'Classic pizza with fresh mozzarella and basil',
                    'is_featured': True
                },
                {
                    'name': 'Chocolate Brownie',
                    'category': dessert_cat,
                    'price': 149.00,
                    'description': 'Rich chocolate brownie with vanilla ice cream',
                    'discount': 15
                },
                {
                    'name': 'Fresh Lime Soda',
                    'category': beverage_cat,
                    'price': 79.00,
                    'description': 'Refreshing lime soda with mint',
                },
            ]
            
            for item_data in sample_items:
                item, created = MenuItem.objects.get_or_create(
                    name=item_data['name'],
                    defaults={
                        'slug': item_data['name'].lower().replace(' ', '-'),
                        'category': item_data['category'],
                        'price': item_data['price'],
                        'description': item_data['description'],
                        'discount': item_data.get('discount', 0),
                        'is_featured': item_data.get('is_featured', False),
                        'available': True
                    }
                )
                if created:
                    self.stdout.write(f'   ✅ Created menu item: {item.name}')

        self.stdout.write(
            self.style.SUCCESS('✅ Sample data created successfully!')
        )
