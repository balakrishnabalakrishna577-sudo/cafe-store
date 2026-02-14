from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cafe.models import Category, MenuItem
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate the database with sample cafe data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create categories
        categories_data = [
            {
                'name': 'Pizza',
                'slug': 'pizza',
                'description': 'Delicious handmade pizzas with fresh ingredients',
                'icon': 'fa-pizza-slice'
            },
            {
                'name': 'Burgers',
                'slug': 'burgers',
                'description': 'Juicy burgers with premium ingredients',
                'icon': 'fa-hamburger'
            },
            {
                'name': 'Beverages',
                'slug': 'beverages',
                'description': 'Refreshing drinks and hot beverages',
                'icon': 'fa-coffee'
            },
            {
                'name': 'Desserts',
                'slug': 'desserts',
                'description': 'Sweet treats and delicious desserts',
                'icon': 'fa-ice-cream'
            }
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create menu items
        pizza_category = Category.objects.get(slug='pizza')
        burger_category = Category.objects.get(slug='burgers')
        beverage_category = Category.objects.get(slug='beverages')
        dessert_category = Category.objects.get(slug='desserts')

        menu_items_data = [
            # Pizzas
            {
                'name': 'Margherita Pizza',
                'slug': 'margherita-pizza',
                'price': Decimal('12.99'),
                'category': pizza_category,
                'description': 'Classic pizza with tomato sauce, mozzarella, and fresh basil',
                'ingredients': 'Tomato sauce, mozzarella cheese, fresh basil, olive oil',
                'item_type': 'veg',
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?w=400&h=300&fit=crop'
            },
            {
                'name': 'Pepperoni Pizza',
                'slug': 'pepperoni-pizza',
                'price': Decimal('15.99'),
                'category': pizza_category,
                'description': 'Classic pepperoni pizza with mozzarella cheese',
                'ingredients': 'Tomato sauce, mozzarella cheese, pepperoni',
                'item_type': 'non-veg',
                'image_url': 'https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400&h=300&fit=crop'
            },
            # Burgers
            {
                'name': 'Classic Cheeseburger',
                'slug': 'classic-cheeseburger',
                'price': Decimal('9.99'),
                'category': burger_category,
                'description': 'Juicy beef patty with cheese, lettuce, tomato, and special sauce',
                'ingredients': 'Beef patty, cheese, lettuce, tomato, onion, special sauce',
                'item_type': 'non-veg',
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop'
            },
            {
                'name': 'Veggie Burger',
                'slug': 'veggie-burger',
                'price': Decimal('8.99'),
                'category': burger_category,
                'description': 'Plant-based patty with fresh vegetables',
                'ingredients': 'Veggie patty, lettuce, tomato, onion, avocado',
                'item_type': 'veg',
                'image_url': 'https://images.unsplash.com/photo-1520072959219-c595dc870360?w=400&h=300&fit=crop'
            },
            # Beverages
            {
                'name': 'Fresh Orange Juice',
                'slug': 'fresh-orange-juice',
                'price': Decimal('4.99'),
                'category': beverage_category,
                'description': 'Freshly squeezed orange juice',
                'ingredients': 'Fresh oranges',
                'item_type': 'veg',
                'image_url': 'https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=400&h=300&fit=crop'
            },
            {
                'name': 'Cappuccino',
                'slug': 'cappuccino',
                'price': Decimal('3.99'),
                'category': beverage_category,
                'description': 'Rich espresso with steamed milk and foam',
                'ingredients': 'Espresso, steamed milk, milk foam',
                'item_type': 'veg',
                'image_url': 'https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=400&h=300&fit=crop'
            },
            # Desserts
            {
                'name': 'Chocolate Cake',
                'slug': 'chocolate-cake',
                'price': Decimal('6.99'),
                'category': dessert_category,
                'description': 'Rich chocolate cake with chocolate frosting',
                'ingredients': 'Chocolate, flour, eggs, butter, sugar',
                'item_type': 'veg',
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=300&fit=crop'
            },
            {
                'name': 'Vanilla Ice Cream',
                'slug': 'vanilla-ice-cream',
                'price': Decimal('4.99'),
                'category': dessert_category,
                'description': 'Creamy vanilla ice cream',
                'ingredients': 'Milk, cream, vanilla, sugar',
                'item_type': 'veg',
                'image_url': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop'
            }
        ]

        for item_data in menu_items_data:
            menu_item, created = MenuItem.objects.get_or_create(
                slug=item_data['slug'],
                defaults=item_data
            )
            if created:
                self.stdout.write(f'Created menu item: {menu_item.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated sample data!')
        )