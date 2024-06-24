from celery import shared_task
from orders.models import Order
from django.core.mail import send_mail


@shared_task
def order_created(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully created.
    """
    order = Order.objects.get(id=order_id)
    subject = f"Order nr. {order.id}"  # type: ignore
    message = """
Dear Mr. {first_name},

You have successfully placed an order of ${total_cost}.
Your Order ID is #{order_id}.

Regards,
Lee's EShop
""".format(
        first_name=order.first_name,
        order_id=order.id,  # type: ignore
        total_cost=order.get_total_cost(),
    )
    mail_sent = send_mail(subject, message, "admin@myshop.com", [order.email])
    return mail_sent
