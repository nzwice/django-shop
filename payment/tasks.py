from io import BytesIO
from celery import shared_task
from django.conf import settings
import weasyprint
from orders.models import Order
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
import os


@shared_task
def payment_completed(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully paid.
    """
    order = Order.objects.get(id=order_id)
    # create invoice e-mail
    subject = f"Lee's EShop  - Invoice no. {order.id}"  # type: ignore
    message = "Please, find attached the invoice for your recent purchase."
    email = EmailMessage(subject, message, "admin@myshop.com", [order.email])
    # generate PDF
    html = render_to_string("orders/order/pdf.html", {"order": order})
    out = BytesIO()
    weasyprint.HTML(string=html).write_pdf(
        out,
        stylesheets=[weasyprint.CSS(os.path.join(settings.STATIC_ROOT, "css/pdf.css"))],
    )  # attach PDF file
    email.attach(
        f"order_{order.id}.pdf", out.getvalue(), "application/pdf"  # type: ignore
    )  # send e-mail
    return email.send()
