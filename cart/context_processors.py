from django.http import HttpRequest
from django.views.decorators.http import require_GET

from cart.cart import Cart


@require_GET
def cart(request: HttpRequest):
    return {"cart": Cart(request)}
