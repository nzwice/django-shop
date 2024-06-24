from django.contrib import admin

from coupons.models import Coupon


# Register your models here.


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    pass
