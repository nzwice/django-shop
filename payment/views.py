from decimal import Decimal
from http import HTTPStatus
from pickle import FALSE
from uu import Error
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from requests import session
import stripe
import logging
from .tasks import payment_completed as payment_completed_task

logger = logging.getLogger(__name__)


from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
def payment_process(request: HttpRequest):
    order_id = request.session.get("order_id", None)
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        success_url = request.build_absolute_uri(reverse("payment:completed"))
        cancel_url = request.build_absolute_uri(reverse("payment:canceled"))
        line_items = []
        # TODO: deactivate order's coupon
        # if order.coupon != None:
        #     order.coupon.active = False
        #     order.coupon.save()
        for item in order.items.all():  # type: ignore
            line_items.append(
                {
                    "price_data": {
                        "unit_amount": int(
                            item.price * Decimal("100")
                        ),  # price * 100 cents
                        "currency": "usd",
                        "product_data": {"name": item.product.name},
                    },
                    "quantity": item.quantity,
                }
            )
        session_data = {
            "mode": "payment",
            "client_reference_id": order.id,  # type: ignore
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": line_items,
        }
        if order.coupon:
            stripe_coupon = stripe.Coupon.create(
                name=order.coupon.code, percent_off=order.discount, duration="once"
            )
            session_data["discounts"] = [{"coupon": stripe_coupon.id}]
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=HTTPStatus.SEE_OTHER.value)  # type: ignore
    else:
        return render(
            request,
            "payment/process.html",
            {
                "order": order,
            },
        )


def payment_completed(request: HttpRequest):
    return render(request, "payment/completed.html")


def payment_canceled(request: HttpRequest):
    return render(request, "payment/canceled.html")


@csrf_exempt
@require_POST
def stripe_webhook(request: HttpRequest):
    event = None
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except Error as evtErr:
        if settings.DEBUG:
            logger.warning("stripe_webhook error", evtErr)
        return HttpResponse(status=HTTPStatus.BAD_REQUEST.value)
    match event.type:
        case "checkout.session.completed":
            session = event.data.object
            if session["mode"] == "payment" and session["payment_status"] == "paid":
                order = get_object_or_404(Order, id=session["client_reference_id"])
                order.paid = True
                order.stripe_payment_intent = session["payment_intent"]
                order.save()
                payment_completed_task.delay(order.id)  # type: ignore
        case _:
            pass
    return HttpResponse(status=HTTPStatus.OK.value)
