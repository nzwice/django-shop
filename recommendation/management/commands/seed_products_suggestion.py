from typing import Any
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser, CommandError
import redis

from recommendation.recommender import Recommender

default_rd_instance = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
)


class Command(BaseCommand):
    help = "Sync order data with redis for products recommendation"

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args: Any, **options: Any) -> str | None:
        rc = Recommender()
        try:
            rc.seed_products_suggestion()
        except Exception as exp:
            raise CommandError(exp)
        self.stdout.write("succesfully sync orders with redis suggestion!")
