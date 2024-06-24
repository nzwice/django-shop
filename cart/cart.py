# type: ignore
from decimal import Decimal
from math import prod
from django.conf import settings
from django.http import HttpRequest
from coupons.models import Coupon

from shop.models import Product


class Cart:
    def __init__(self, request: HttpRequest):
        self.session = request.session
        self.cart = self.session.get(settings.CART_SESSION_ID)
        if not self.cart:
            self.cart = self.session[settings.CART_SESSION_ID] = {}
        self.coupon_id = self.session.get("coupon_id")

    @property
    def coupon(self) -> Coupon | None:
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def add(self, product: Product, quantity: int = 1, override: bool = False):
        product_id = self.__get_product_id_str(product)
        if product_id not in self.cart:
            self.cart[product_id] = {
                "quantity": quantity,
                "price_str": str(product.price),
            }
        else:
            if override:
                self.cart[product_id]["quantity"] = quantity
            else:
                self.cart[product_id]["quantity"] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product: Product):
        product_id = self.__get_product_id_str(product)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        id_list = self.cart.keys()
        products = Product.objects.filter(id__in=id_list)
        cart_with_details = self.cart.copy()
        for product in products:
            product_id = self.__get_product_id_str(product)
            cart_with_details[product_id]["product"] = product
            cart_with_details[product_id]["price"] = Decimal(
                cart_with_details[product_id]["price_str"]
            )
            cart_with_details[product_id]["total_price"] = (
                cart_with_details[product_id]["price"]
                * cart_with_details[product_id]["quantity"]
            )
            yield cart_with_details[product_id]

    def __len__(self):
        return len(self.cart)

    def get_total_quantity(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            item["quantity"] * Decimal(item["price_str"]) for item in self.cart.values()
        )

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.cart.clear()
        self.save()

    def __get_product_id_str(self, product: Product):
        return str(product.id)
