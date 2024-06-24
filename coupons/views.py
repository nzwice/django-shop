from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils import timezone

from coupons.forms import CouponApplyForm
from coupons.models import Coupon
from django.views.decorators.http import require_POST


@require_POST
def coupon_apply(request: HttpRequest):
    now = timezone.now()
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data["code"]
        try:
            coupon = Coupon.objects.get(
                code__iexact=code,
                valid_from__lte=now,
                valid_to__gte=now,
                active=True,
            )
            request.session["coupon_id"] = coupon.id  # type: ignore
        except Coupon.DoesNotExist:
            request.session["coupon_id"] = None
    return redirect("cart:cart_detail")
