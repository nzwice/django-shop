from tkinter import NO
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from cart.forms import CartAddProductForm
from recommendation.recommender import Recommender

from shop.models import Category, Product
from django.utils.translation import gettext_lazy as _

# Create your views here.


def product_list(request: HttpRequest, category_slug=None):
    products = Product.objects.filter(available=True).order_by("-image", "price")
    categories = Category.objects.all()
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(
        request,
        "shop/product/list.html",
        {
            "category": category,
            "categories": categories,
            "products": products,
        },
    )


def product_detail(request: HttpRequest, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    rc = Recommender()
    recommended_products = rc.suggest_products_for([product])
    return render(
        request,
        "shop/product/detail.html",
        {
            "product": product,
            "cart_product_form": cart_product_form,
            "recommended_products": recommended_products,
        },
    )
