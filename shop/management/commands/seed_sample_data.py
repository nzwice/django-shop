import collections
import json
from typing import Any, List
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from shop.models import Category, Product


class Command(BaseCommand):
    help = "Seed sample data for the shop"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--json", type=str)

    def handle(self, *args: Any, **options: Any) -> str | None:
        json_file_path = options["json"]
        with open(json_file_path, "r") as f:
            shop_data = json.loads(
                f.read(), object_hook=lambda d: collections.defaultdict(**d)
            )
            categories = shop_data["categories"] or []
            products = shop_data["products"] or []
            self.save_categories(categories)
            self.save_products(products)

    def save_categories(self, categories: List[Any]):
        with transaction.atomic():
            for category in categories:
                if not category["slug"]:
                    continue
                category_data = {
                    "name": category["name"],
                    "slug": category["slug"],
                }
                Category.objects.update_or_create(
                    slug=category["slug"],
                    defaults=category_data,
                )

    def save_products(self, products: List[Any]):
        with transaction.atomic():
            for product in products:
                if not product["slug"]:
                    continue
                category_slug = product["category_slug"]
                product_data = {
                    "name": product["name"],
                    "slug": product["slug"],
                    "description": product["description"],
                    "price": product["price"],
                    "available": product["available"] or True,
                }
                category = Category.objects.filter(slug=category_slug).first()
                if not category:
                    continue
                Product.objects.update_or_create(
                    slug=product["slug"],
                    defaults={**product_data, "category_id": category.id},  # type: ignore
                )
