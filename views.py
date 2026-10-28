from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Product


def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    cart[product_id] = cart.get(product_id, 0) + 1

    request.session['cart'] = cart

    return redirect('home')


def cart(request):
    cart_data = request.session.get('cart', {})
    products = []
    total = 0

    for product_id, quantity in cart_data.items():
        product = Product.objects.get(id=product_id)

        item_total = product.price * quantity
        total += item_total

        products.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total
        })

    return render(request, 'store/cart.html', {
        'products': products,
        'total': total
    })


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart

    return redirect('cart')


def increase_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1

    request.session['cart'] = cart

    return redirect('cart')


def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        if cart[product_id] > 1:
            cart[product_id] -= 1
        else:
            del cart[product_id]

    request.session['cart'] = cart

    return redirect('cart')


def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)

    return render(request, 'store/product_detail.html', {
        'product': product
    })


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'store/register.html', {
                'error': 'Username already exists'
            })

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect('login')

    return render(request, 'store/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        return render(request, 'store/login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'store/login.html')


def user_logout(request):
    logout(request)
    return redirect('home')

def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')

    cart_data = request.session.get('cart', {})

    if not cart_data:
        return redirect('cart')

    products = []
    total = 0

    for product_id, quantity in cart_data.items():
        product = Product.objects.get(id=product_id)

        item_total = product.price * quantity
        total += item_total

        products.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total
        })

    if request.method == 'POST':
        address = request.POST['address']

        from .models import Order

        for item in products:
            Order.objects.create(
                user=request.user,
                product=item['product'],
                quantity=item['quantity'],
                total_price=item['item_total'],
                address=address
            )

        request.session['cart'] = {}

        return render(request, 'store/order_success.html')

    return render(request, 'store/checkout.html', {
        'products': products,
        'total': total
    })