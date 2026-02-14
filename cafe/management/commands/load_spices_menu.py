from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from cafe.models import Category, MenuItem


class Command(BaseCommand):
    """
    Replace existing categories and menu items with the
    Spices of India Cuisine menu provided by the client.
    """

    help = "Load Spices of India Cuisine menu (replaces all existing categories and menu items)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Removing existing menu items and categories..."))
        MenuItem.objects.all().delete()
        Category.objects.all().delete()

        # Define categories
        categories = [
            ("Street Starters & Appetizers", "fa-utensils"),
            ("Indian Kati Rolls", "fa-burrito"),
            ("Curry Bowls (Served with Rice)", "fa-bowl-food"),
            ("Sides & Breads", "fa-bread-slice"),
            ("Drinks", "fa-glass-water"),
        ]

        category_map = {}
        for name, icon in categories:
            cat = Category.objects.create(
                name=name,
                slug=slugify(name),
                description="",
                icon=icon,
            )
            category_map[name] = cat

        def create_item(name, category_name, price, description, item_type="non-veg", is_featured=False):
            category = category_map[category_name]
            base_slug = slugify(name)
            slug = base_slug
            counter = 1
            while MenuItem.objects.filter(slug=slug).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"

            return MenuItem.objects.create(
                name=name,
                slug=slug,
                price=Decimal(str(price)),
                category=category,
                description=description,
                ingredients="",
                item_type=item_type,
                is_featured=is_featured,
                available=True,
            )

        # Street Starters & Appetizers
        starters = "Street Starters & Appetizers"

        create_item(
            name="Samosa (3 pcs)",
            category_name=starters,
            price=3.99,
            description="Crisp, golden pastries filled with spiced potatoes and peas, fried to perfection.",
            item_type="veg",
            is_featured=True,
        )

        create_item(
            name="Samosa Chaat",
            category_name=starters,
            price=6.49,
            description="Crushed samosas topped with chickpeas, yogurt, fresh onions, tangy chutneys, and mild spices.",
            item_type="veg",
            is_featured=True,
        )

        create_item(
            name="Masala Loaded Fries - Paneer (Veg)",
            category_name=starters,
            price=9.99,
            description="Crispy fries topped with paneer, onions, peppers, and flavorful house sauces.",
            item_type="veg",
        )

        create_item(
            name="Masala Loaded Fries - Chicken",
            category_name=starters,
            price=9.99,
            description="Crispy fries topped with chicken, onions, peppers, and flavorful house sauces.",
            item_type="non-veg",
        )

        create_item(
            name="Masala Loaded Fries - Shrimp",
            category_name=starters,
            price=11.99,
            description="Crispy fries topped with shrimp, onions, peppers, and flavorful house sauces.",
            item_type="non-veg",
        )

        create_item(
            name="Indian Chicken Wings (6 pcs)",
            category_name=starters,
            price=9.99,
            description=(
                "Juicy wings tossed in Manchurian, Sweet Chili, or Olive & Garlic dry rub. "
                "Served with French fries."
            ),
            item_type="non-veg",
            is_featured=True,
        )

        create_item(
            name="Indian Boneless Chicken",
            category_name=starters,
            price=11.99,
            description=(
                "Tender boneless chicken pieces cooked in your choice of sauce: "
                "Tikka Masala, Manchurian, Chilli, 65, or Karampodi."
            ),
            item_type="non-veg",
        )

        create_item(
            name="Tikka Grill - Paneer (Veg)",
            category_name=starters,
            price=11.49,
            description="Paneer marinated and grilled over flame for a smoky, delicious flavor.",
            item_type="veg",
        )

        create_item(
            name="Tikka Grill - Chicken",
            category_name=starters,
            price=10.99,
            description="Chicken marinated and grilled over flame for a smoky, delicious flavor.",
            item_type="non-veg",
        )

        create_item(
            name="Tikka Grill - Shrimp",
            category_name=starters,
            price=12.99,
            description="Shrimp marinated and grilled over flame for a smoky, delicious flavor.",
            item_type="non-veg",
        )

        # Indian Kati Rolls
        rolls = "Indian Kati Rolls"

        create_item(
            name="Indian Kati Roll - Paneer (Veg)",
            category_name=rolls,
            price=10.49,
            description=(
                "Soft flatbread wrapped around spiced paneer with onions, peppers, and sauces. "
                "Served with fries."
            ),
            item_type="veg",
            is_featured=True,
        )

        create_item(
            name="Indian Kati Roll - Chicken",
            category_name=rolls,
            price=9.99,
            description=(
                "Soft flatbread wrapped around spiced chicken with onions, peppers, and sauces. "
                "Served with fries."
            ),
            item_type="non-veg",
        )

        create_item(
            name="Indian Kati Roll - Shrimp",
            category_name=rolls,
            price=11.99,
            description=(
                "Soft flatbread wrapped around spiced shrimp with onions, peppers, and sauces. "
                "Served with fries."
            ),
            item_type="non-veg",
        )

        # Curry Bowls (Served with Rice)
        bowls = "Curry Bowls (Served with Rice)"

        create_item(
            name="Butter Chicken",
            category_name=bowls,
            price=13.99,
            description="Chicken simmered in a creamy tomato sauce with mild, aromatic spices. Served with rice.",
            item_type="non-veg",
            is_featured=True,
        )

        create_item(
            name="Chicken Tikka Masala",
            category_name=bowls,
            price=13.99,
            description="Grilled chicken in a smooth tomato cream sauce, rich and comforting. Served with rice.",
            item_type="non-veg",
        )

        create_item(
            name="Lamb Curry",
            category_name=bowls,
            price=16.49,
            description="Tender lamb slowly cooked in traditional spices for a hearty flavor. Served with rice.",
            item_type="non-veg",
        )

        create_item(
            name="Chicken Curry",
            category_name=bowls,
            price=13.99,
            description="Homestyle chicken curry with fresh herbs and spices. Served with rice.",
            item_type="non-veg",
        )

        create_item(
            name="Biryani Bowl - Paneer (Veg)",
            category_name=bowls,
            price=10.99,
            description=(
                "Fragrant, layered rice with paneer, cooked with aromatic spices. "
                "Served as a complete bowl."
            ),
            item_type="veg",
        )

        create_item(
            name="Biryani Bowl - Chicken",
            category_name=bowls,
            price=11.99,
            description=(
                "Fragrant, layered rice with chicken, cooked with aromatic spices. "
                "Served as a complete bowl."
            ),
            item_type="non-veg",
        )

        create_item(
            name="Biryani Bowl - Lamb",
            category_name=bowls,
            price=12.99,
            description=(
                "Fragrant, layered rice with lamb, cooked with aromatic spices. "
                "Served as a complete bowl."
            ),
            item_type="non-veg",
        )

        create_item(
            name="Paneer Tikka Masala (Veg)",
            category_name=bowls,
            price=11.99,
            description="Grilled paneer cubes in a creamy tomato sauce with warm spices. Served with rice.",
            item_type="veg",
        )

        create_item(
            name="Veg Korma (Veg)",
            category_name=bowls,
            price=10.49,
            description="Mixed vegetables cooked in a mild, creamy coconut-based sauce. Served with rice.",
            item_type="veg",
        )

        create_item(
            name="Channa Masala (Veg)",
            category_name=bowls,
            price=9.99,
            description="Chickpeas simmered in a gently spiced tomato and onion gravy. Served with rice.",
            item_type="veg",
        )

        # Sides & Breads
        sides = "Sides & Breads"

        create_item(
            name="Plain Naan",
            category_name=sides,
            price=1.99,
            description="Soft, pillowy flatbread.",
            item_type="veg",
        )

        create_item(
            name="Butter Naan",
            category_name=sides,
            price=2.49,
            description="Soft, pillowy flatbread brushed with butter.",
            item_type="veg",
        )

        create_item(
            name="Garlic Naan",
            category_name=sides,
            price=2.99,
            description="Naan infused with fresh garlic and butter.",
            item_type="veg",
        )

        create_item(
            name="Cheese Naan",
            category_name=sides,
            price=3.99,
            description="Naan filled with melted cheese for a rich, comforting flavor.",
            item_type="veg",
        )

        create_item(
            name="Dum Rice",
            category_name=sides,
            price=3.99,
            description="Slow-steamed aromatic rice with gentle spices.",
            item_type="veg",
        )

        # Drinks
        drinks = "Drinks"

        create_item(
            name="Mango Lassi",
            category_name=drinks,
            price=5.49,
            description="Smooth, creamy yogurt-based mango drink.",
            item_type="veg",
            is_featured=True,
        )

        create_item(
            name="Soda",
            category_name=drinks,
            price=1.50,
            description="Choice of Coke, Sprite, or Dr Pepper.",
            item_type="veg",
        )

        self.stdout.write(self.style.SUCCESS("Spices of India Cuisine menu loaded successfully."))

