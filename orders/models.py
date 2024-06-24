from decimal import Decimal
from django.conf import settings
from django.db import models
from coupons.models import Coupon
from django.core.validators import MinValueValidator, MaxValueValidator

from shop.models import Product


# Create your models here.
class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=50)
    city = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    coupon = models.ForeignKey(
        Coupon, related_name="orders", null=True, blank=True, on_delete=models.SET_NULL
    )
    discount = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    class Meta:
        pass

    def __str__(self) -> str:
        return f"Order #{self.id}"  # type: ignore

    def get_total_cost(self) -> Decimal:
        return self.get_total_cost_before_discount() - self.get_discount()

    def get_total_cost_before_discount(self) -> Decimal:
        return sum(item.get_cost() for item in self.items.all())  # type: ignore

    def get_discount(self):
        if self.discount:
            total_cost = self.get_total_cost_before_discount()
            return total_cost * Decimal(self.discount) / Decimal(100)
        return Decimal(0)

    def get_stripe_url(self):
        if not self.stripe_payment_intent:
            # no payment associated
            return ""
        if "_test_" in settings.STRIPE_SECRET_KEY:
            # Stripe path for test payments
            path = "/test/"
        else:
            # Stripe path for real payments
            path = "/"
        return (
            f"https://dashboard.stripe.com{path}payments/{self.stripe_payment_intent}"
        )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="order_items", on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        pass

    def __str__(self) -> str:
        return f"Order #{self.order.id} - Product #{self.product.id}"  # type: ignore

    def get_cost(self):
        return self.price * self.quantity
