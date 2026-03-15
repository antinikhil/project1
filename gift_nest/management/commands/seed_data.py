from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from gift_nest.models import Category, Product, Customer, DeliveryPerson, Offer, Order, OrderItem
from decimal import Decimal
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # 1. Create Groups
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        delivery_group, _ = Group.objects.get_or_create(name='Delivery')

        # 2. Create Users
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@giftnest.com', 'admin123')
            admin_user.groups.add(admin_group)
            self.stdout.write('Created admin user')

        if not User.objects.filter(username='delivery1').exists():
            d_user = User.objects.create_user('delivery1', 'delivery1@giftnest.com', 'delivery123')
            d_user.groups.add(delivery_group)
            DeliveryPerson.objects.create(user=d_user, phone_number='9876543210', vehicle_number='GIFT-01')
            self.stdout.write('Created delivery person')

        if not User.objects.filter(username='customer1').exists():
            c_user = User.objects.create_user('customer1', 'customer1@giftnest.com', 'customer123')
            Customer.objects.create(user=c_user, phone_number='1234567890', address='456 Rose Lane, Blossom City')
            self.stdout.write('Created customer')

        # 3. Create Categories
        cat_flowers, _ = Category.objects.update_or_create(
            name='Flowers', 
            defaults={
                'description': 'Fresh and beautiful floral arrangements',
                'image_url': 'https://images.unsplash.com/photo-1490750967868-88815ad623b7?q=80&w=2070&auto=format&fit=crop'
            }
        )
        cat_cakes, _ = Category.objects.update_or_create(
            name='Cakes', 
            defaults={
                'description': 'Delicious cakes for all celebrations',
                'image_url': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?q=80&w=1989&auto=format&fit=crop'
            }
        )
        cat_personalized, _ = Category.objects.update_or_create(
            name='Personalized Gifts', 
            defaults={
                'description': 'Customized gifts with a personal touch',
                'image_url': 'https://images.unsplash.com/photo-1585515320310-259814833e62?q=80&w=2070&auto=format&fit=crop'
            }
        )
        cat_combos, _ = Category.objects.update_or_create(
            name='Gift Combos', 
            defaults={
                'description': 'Perfectly paired sets for any occasion',
                'image_url': 'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?q=80&w=2040&auto=format&fit=crop'
            }
        )

        # 4. Create Products
        Product.objects.update_or_create(
            name='Royal Red Roses',
            defaults={
                'category': cat_flowers,
                'description': 'A stunning bouquet of 12 premium red roses with seasonal fillers.',
                'price': Decimal('45.99'),
                'stock_quantity': 100,
                'rating': 4.8,
                'image_url': 'https://images.unsplash.com/photo-1548849170-350562ca0919?q=80&w=1974&auto=format&fit=crop'
            }
        )
        Product.objects.update_or_create(
            name='Velvet Chocolate Delight',
            defaults={
                'category': cat_cakes,
                'description': 'Rich dark chocolate cake with smooth ganache topping. (1kg)',
                'price': Decimal('35.00'),
                'stock_quantity': 50,
                'rating': 4.9,
                'image_url': 'https://images.unsplash.com/photo-1588195538326-c5b1e9f80a1b?q=80&w=1950&auto=format&fit=crop'
            }
        )
        Product.objects.update_or_create(
            name='Custom Photo Mug',
            defaults={
                'category': cat_personalized,
                'description': 'High-quality ceramic mug with your favorite photo printed.',
                'price': Decimal('15.50'),
                'stock_quantity': 200,
                'rating': 4.5,
                'image_url': 'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?q=80&w=2070&auto=format&fit=crop'
            }
        )
        Product.objects.update_or_create(
            name='Classic Celebration Combo',
            defaults={
                'category': cat_combos,
                'description': 'A bouquet of lilies paired with 1/2kg chocolate cake.',
                'price': Decimal('65.00'),
                'stock_quantity': 30,
                'rating': 4.7,
                'image_url': 'https://images.unsplash.com/photo-1513201099705-a9746e1e201f?q=80&w=1974&auto=format&fit=crop'
            }
        )

        # 5. Create Offers
        Offer.objects.update_or_create(
            code='SPRING20',
            defaults={
                'title': 'Spring Sale',
                'description': 'Get 20% off on all floral gifts!',
                'discount_percentage': Decimal('20.00'),
                'valid_from': timezone.now(),
                'valid_to': timezone.now() + datetime.timedelta(days=30),
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database'))
