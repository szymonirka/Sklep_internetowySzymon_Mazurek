from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, CartItem, Order, Payment, Category
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from django.http import HttpResponse
from django.contrib.auth.views import LogoutView

def home(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = None
    categories = Category.objects.filter(parent__isnull=True)
    return render(request, 'home.html', {'categories': categories, 'products': products, 'query': query})

# views.py
def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subcategories = category.subcategories.all()
    query = request.GET.get('q')
    if query:
        products = category.products.filter(name__icontains=query)
    else:
        products = category.products.all()
    return render(request, 'category_products.html', {'category': category, 'products': products, 'subcategories': subcategories, 'query': query})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    images = product.images.all()
    return render(request, 'product_detail.html', {'product': product, 'images': images})

def search_results(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.none()
    return render(request, 'search_results.html', {'products': products, 'query': query})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')

@login_required
def view_cart(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.all()
    total_sum = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'view_cart.html', {'cart_items': cart_items, 'total_sum': total_sum})

@login_required
def remove_from_cart(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    try:
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        cart_item.delete()
    except CartItem.DoesNotExist:
        # Handle the case where the cart item does not exist
        pass
    return redirect('view_cart')

@login_required
def increase_quantity(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    try:
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        # Handle the case where the cart item does not exist
        pass
    return redirect('view_cart')

@login_required
def decrease_quantity(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    try:
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        # Handle the case where the cart item does not exist
        pass
    return redirect('view_cart')


# views.py
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart.items.all())
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            payment_method=request.POST['payment_method'],
            shipping_method=request.POST['shipping_method'],
            street_address=request.POST['street_address'],
            postal_code=request.POST['postal_code'],
            city=request.POST['city'],
            country=request.POST['country'],
            phone_number=request.POST['phone_number']
        )
        if 'invoice' in request.POST:
            order.company_name = request.POST['company_name']
            order.company_address = request.POST['company_address']
            order.vat_number = request.POST['vat_number']
            order.contact = request.POST['contact']
            order.bank_account = request.POST['bank_account']
            order.email = request.POST['email']
            order.save()
        for item in cart.items.all():
            item.order = order
            item.save()
        return redirect('payment', order_id=order.id)
    return render(request, 'checkout.html', {'cart': cart, 'total_price': total_price})

@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payment.html', {'order': order})

# views.py
@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = get_object_or_404(Cart, user=request.user)
    # Implement payment processing logic here
    if request.method == 'POST':
        # Assuming payment is successful
        order.is_paid = True
        order.save()
        cart.items.all().delete()  # Clear the cart items after payment is processed
        return redirect('order_confirmation', order_id=order.id)
    return render(request, 'process_payment.html', {'order': order})

# views.py
@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})

@login_required
def user_profile(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'user_profile.html', {'user': request.user, 'orders': orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.status = 'Cancelled'
    order.save()
    return redirect('user_profile')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return render(request, 'logout.html')