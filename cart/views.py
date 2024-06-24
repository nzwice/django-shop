from django.http import HttpRequest
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render

from cart.cart import Cart
from cart.forms import CartAddProductForm
from coupons.forms import CouponApplyForm
from recommendation.recommender import Recommender
from shop.models import Product

# Create your views here.


@require_POST
def cart_add(request: HttpRequest, product_id):
    cart = Cart(request=request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        cart.add(
            product=product,
            quantity=cleaned_data["quantity"],
            override=cleaned_data["override"],
        )
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request: HttpRequest, product_id):
    cart = Cart(request=request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product=product)
    return redirect("cart:cart_detail")


def cart_detail(request: HttpRequest):
    cart = Cart(request=request)
    for item in cart:
        item["update_quantity_form"] = CartAddProductForm(
            initial={"quantity": item["quantity"], "override": True}
        )
    coupon_apply_form = CouponApplyForm()
    rc = Recommender()
    cart_products = [item["product"] for item in cart]
    if cart_products:
        recommended_products = rc.suggest_products_for(cart_products)
    else:
        recommended_products = []
    return render(
        request,
        "cart/detail.html",
        {
            "cart": cart,
            "coupon_apply_form": coupon_apply_form,
            "recommended_products": recommended_products,
        },
    )
