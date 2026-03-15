from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, Product, Customer, Order, OrderItem, Cart
from decimal import Decimal

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.customer = Customer.objects.create(user=self.user, phone_number='1234567890', address='123 Test St')
        self.category = Category.objects.create(name='Flowers', description='Fresh flowers')
        self.product = Product.objects.create(
            category=self.category,
            name='Red Roses',
            description='A bouquet of red roses',
            price=Decimal('29.99'),
            stock_quantity=50
        )

    def test_category_creation(self):
        self.assertEqual(str(self.category), 'Flowers')
        self.assertEqual(self.category.name, 'Flowers')

    def test_product_creation(self):
        self.assertEqual(str(self.product), 'Red Roses')
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.price, Decimal('29.99'))

    def test_customer_creation(self):
        self.assertEqual(str(self.customer), 'testuser')
        self.assertEqual(self.customer.phone_number, '1234567890')

    def test_order_and_orderitem(self):
        order = Order.objects.create(
            customer=self.customer,
            total_amount=Decimal('29.99'),
            shipping_address='123 Test St'
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=self.product.price
        )
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order.status, 'Pending')

    def test_cart_functionality(self):
        cart_item = Cart.objects.create(
            customer=self.customer,
            product=self.product,
            quantity=2
        )
        self.assertEqual(Cart.objects.count(), 1)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.customer, self.customer)
