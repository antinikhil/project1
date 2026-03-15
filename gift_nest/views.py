from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum, Count
from .models import *
from .forms import *  # I'll create forms.py next
from django.utils import timezone
from django.http import HttpResponse

# Helper decorators
def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()

def is_delivery_person(user):
    try:
        return user.delivery_profile is not None
    except:
        return False

def is_customer(user):
    try:
        return user.customer_profile is not None
    except:
        return False

# --- VISITOR VIEWS ---

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_available=True)[:8]
    offers = Offer.objects.filter(is_active=True, valid_to__gte=timezone.now())
    return render(request, 'gift_nest/home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'offers': offers
    })

def product_list(request, category_id=None):
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        products = products.filter(category=category)
    return render(request, 'gift_nest/product_list.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    feedbacks = product.feedbacks.all()
    return render(request, 'gift_nest/product_detail.html', {
        'product': product,
        'feedbacks': feedbacks
    })

def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_available=True
    )
    return render(request, 'gift_nest/product_list.html', {'products': products, 'search_query': query})

def offers_page(request):
    offers = Offer.objects.filter(is_active=True, valid_to__gte=timezone.now())
    return render(request, 'gift_nest/offers.html', {'offers': offers})

# --- AUTH VIEWS ---

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user=user, phone_number=form.cleaned_data.get('phone_number'), address=form.cleaned_data.get('address'))
            messages.success(request, "Account created successfully. You can now login.")
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'gift_nest/register.html', {'form': form})

def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                if is_admin(user):
                    return redirect('admin_dashboard')
                elif is_delivery_person(user):
                    return redirect('delivery_dashboard')
                else:
                    return redirect('customer_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'gift_nest/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

# --- CUSTOMER VIEWS ---

@login_required
def customer_dashboard(request):
    customer = request.user.customer_profile
    orders = Order.objects.filter(customer=customer).order_by('-order_date')[:5]
    return render(request, 'gift_nest/customer/dashboard.html', {'orders': orders})

@login_required
def cart_page(request):
    customer = request.user.customer_profile
    cart_items = Cart.objects.filter(customer=customer)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'gift_nest/customer/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    customer = request.user.customer_profile
    customization = request.POST.get('customization', '')
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, created = Cart.objects.get_or_create(customer=customer, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.customization_text = customization
    cart_item.save()
    messages.success(request, f"{product.name} added to cart.")
    return redirect('cart_page')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, customer=request.user.customer_profile)
    cart_item.delete()
    return redirect('cart_page')

@login_required
def checkout_page(request):
    customer = request.user.customer_profile
    cart_items = Cart.objects.filter(customer=customer)
    if not cart_items:
        return redirect('product_list')
        
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == '123456':
            order = Order.objects.create(
                customer=customer,
                total_amount=total,
                shipping_address=customer.address,
                status='Placed',
                is_paid=True
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                    customization_text=item.customization_text
                )
                # Update stock
                item.product.stock_quantity -= item.quantity
                item.product.save()
            
            Payment.objects.create(
                order=order,
                amount=total,
                payment_mode='Card',
                transaction_id=f"TRANS_{order.id}_{timezone.now().timestamp()}"
            )
            
            cart_items.delete()
            messages.success(request, "Order placed successfully!")
            return redirect('order_history')
        else:
            messages.error(request, "Invalid OTP. Please use 123456.")
            
    return render(request, 'gift_nest/customer/checkout.html', {'total': total})

@login_required
def order_history(request):
    customer = request.user.customer_profile
    orders = Order.objects.filter(customer=customer).order_by('-order_date')
    return render(request, 'gift_nest/customer/order_history.html', {'orders': orders})

@login_required
def track_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer_profile)
    assignment = getattr(order, 'delivery_assignment', None)
    return render(request, 'gift_nest/customer/track_delivery.html', {'order': order, 'assignment': assignment})

@login_required
def profile_page(request):
    customer = request.user.customer_profile
    if request.method == 'POST':
        customer.phone_number = request.POST.get('phone_number')
        customer.address = request.POST.get('address')
        customer.save()
        messages.success(request, "Profile updated.")
    return render(request, 'gift_nest/customer/profile.html', {'customer': customer})

@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer_profile)
    return render(request, 'gift_nest/customer/invoice.html', {'order': order})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer_profile)
    if order.status in ['Pending', 'Placed']:
        order.status = 'Cancelled'
        order.save()
        messages.success(request, "Order cancelled.")
    return redirect('order_history')

@login_required
def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer_profile)
    if order.status == 'Delivered':
        ReturnOrder.objects.get_or_create(order=order, reason="Customer requested return")
        messages.success(request, "Return request submitted.")
    return redirect('order_history')

# --- ADMIN VIEWS ---

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(is_paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_customers = Customer.objects.count()
    recent_orders = Order.objects.order_by('-order_date')[:10]
    return render(request, 'gift_nest/admin/dashboard.html', {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'recent_orders': recent_orders
    })

@user_passes_test(is_admin)
def manage_products(request):
    products = Product.objects.all()
    return render(request, 'gift_nest/admin/products.html', {'products': products})

@user_passes_test(is_admin)
def manage_categories(request):
    categories = Category.objects.all()
    return render(request, 'gift_nest/admin/categories.html', {'categories': categories})

@user_passes_test(is_admin)
def manage_stock(request):
    products = Product.objects.all()
    return render(request, 'gift_nest/admin/stock.html', {'products': products})

@user_passes_test(is_admin)
def manage_orders(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'gift_nest/admin/orders.html', {'orders': orders})

@user_passes_test(is_admin)
def manage_customers(request):
    customers = Customer.objects.all()
    return render(request, 'gift_nest/admin/customers.html', {'customers': customers})

@user_passes_test(is_admin)
def manage_delivery(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        delivery_person_id = request.POST.get('delivery_person_id')
        order = get_object_or_404(Order, id=order_id)
        delivery_person = get_object_or_404(DeliveryPerson, id=delivery_person_id)
        
        DeliveryAssignment.objects.update_or_create(
            order=order,
            defaults={'delivery_person': delivery_person, 'status': 'Assigned'}
        )
        order.status = 'Shipped'
        order.save()
        messages.success(request, f"Order #{order_id} assigned successfully.")
        return redirect('manage_delivery')

    assignments = DeliveryAssignment.objects.all()
    delivery_persons = DeliveryPerson.objects.filter(is_available=True)
    return render(request, 'gift_nest/admin/delivery.html', {'assignments': assignments, 'delivery_persons': delivery_persons})

@user_passes_test(is_admin)
def reports_page(request):
    # Basic report data
    order_stats = Order.objects.values('status').annotate(count=Count('id'))
    product_stats = Product.objects.values('category__name').annotate(count=Count('id'))
    return render(request, 'gift_nest/admin/reports.html', {
        'order_stats': order_stats,
        'product_stats': product_stats
    })

# --- DELIVERY VIEWS ---

@user_passes_test(is_delivery_person)
def delivery_dashboard(request):
    delivery_person = request.user.delivery_profile
    pending_deliveries = DeliveryAssignment.objects.filter(delivery_person=delivery_person, status__in=['Assigned', 'Picked Up', 'In Transit'])
    return render(request, 'gift_nest/delivery/dashboard.html', {'pending_deliveries': pending_deliveries})

@user_passes_test(is_delivery_person)
def assigned_orders(request):
    delivery_person = request.user.delivery_profile
    assignments = DeliveryAssignment.objects.filter(delivery_person=delivery_person)
    return render(request, 'gift_nest/delivery/assignments.html', {'assignments': assignments})

@user_passes_test(is_delivery_person)
def update_delivery_status(request, assignment_id):
    assignment = get_object_or_404(DeliveryAssignment, id=assignment_id, delivery_person=request.user.delivery_profile)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        assignment.status = new_status
        assignment.save()
        
        # Update linked order status
        if new_status == 'Delivered':
            assignment.order.status = 'Delivered'
        elif new_status == 'Picked Up':
            assignment.order.status = 'Out for Delivery'
        assignment.order.save()
        
        messages.success(request, "Delivery status updated.")
        return redirect('delivery_dashboard')
    return render(request, 'gift_nest/delivery/update_status.html', {'assignment': assignment})
