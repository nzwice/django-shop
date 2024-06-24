import html
from http import HTTPStatus
from itertools import product
from turtle import delay
from django.conf import Settings, settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
import stripe
import weasyprint

from cart.cart import Cart
from orders.forms import OrderCreateForm
from orders.models import Order, OrderItem
from django.db import transaction

from orders.tasks import order_created

# Create your views here.


@transaction.atomic
def order_create(request: HttpRequest):
    cart = Cart(request=request)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)  # type: ignore
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )
            cart.clear()
            order_created.delay(order.id)
            request.session["order_id"] = order.id
            return redirect(reverse("payment:process"))
        return HttpResponse("Bad Request!", status=HTTPStatus.BAD_REQUEST)
    else:
        form = OrderCreateForm()
        return render(
            request,
            "orders/order/create.html",
            {"form": form},
        )


@staff_member_required
def staff_order_pdf(request: HttpRequest, order_id):
    order = get_object_or_404(Order, id=order_id)
    pdf_html_str = render_to_string("orders/order/pdf.html", {"order": order})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename=order_{order.id}.pdf"  # type: ignore
    weasyprint.HTML(string=pdf_html_str).write_pdf(
        response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / "css/pdf.css")]
    )
    return response
