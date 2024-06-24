from collections import defaultdict
from itertools import groupby, product
from math import prod
import typing
from django.conf import settings
import redis
from orders.models import Order, OrderItem

from shop.models import Product

default_rd_instance = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
)


class Recommender:
    def __init__(self) -> None:
        self.rd = default_rd_instance

    def get_ranked_product_key(self, product_id: str):
        return f"product:{product_id}:purchased_with"

    def save_products_bought_together(self, products: typing.List[Product]):
        product_ids = [p.id for p in products]  # type: ignore
        for product_id in product_ids:
            for other_id in product_ids:
                if product_id != other_id:
                    self.rd.zincrby(
                        self.get_ranked_product_key(product_id), 1, other_id
                    )

    def suggest_products_for(
        self,
        products: typing.List[Product],
        max_results=6,
    ) -> typing.List[Product]:
        product_ids = [product.id for product in products]  # type: ignore
        ranked_keys = [
            self.get_ranked_product_key(product_id) for product_id in product_ids
        ]
        tmp_key = f"tmp_{';'.join(str(pid) for pid in product_ids)}"
        self.rd.zunionstore(tmp_key, ranked_keys, "SUM")
        self.rd.zrem(tmp_key, *product_ids)
        suggested_ids = self.rd.zrange(tmp_key, 0, -1, desc=True)[:max_results]  # type: ignore
        suggested_ids = [str(sid, encoding="utf-8") for sid in suggested_ids]
        self.rd.delete(tmp_key)
        suggested_products = list(
            Product.objects.filter(
                id__in=suggested_ids,
            )
        )
        suggested_products.sort(key=lambda p: suggested_ids.index(str(p.id)))  # type: ignore
        return suggested_products

    def clear_suggetions(self):
        for product_id in Product.objects.values_list("id", flat=True):
            self.rd.delete(self.get_ranked_product_key(product_id))

    def seed_products_suggestion(self):
        """
        This function sync all products from all orders to redis DB for initial suggestions.
        It's a long running operation and should be used by management command only.
        """
        self.clear_suggetions()
        items = list(OrderItem.objects.select_related("product"))
        orders = defaultdict(list)
        for item in items:
            orders[item.order_id].append(item.product)  # type: ignore
        for products in orders.values():  # type: ignore
            self.save_products_bought_together(products)  # type: ignore
