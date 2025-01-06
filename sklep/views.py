from django.shortcuts import render, get_object_or_404
from .models import Category, Product


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