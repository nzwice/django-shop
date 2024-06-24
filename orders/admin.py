import datetime
from time import strftime
from typing import Any
from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet
from django.utils.safestring import mark_safe
import csv

from django.urls import reverse
from orders.models import Order, OrderItem

# Register your models here.


def export_to_csv(
    model_admin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
) -> HttpResponse:
    model_metadata = model_admin.model._meta
    response = HttpResponse(content_type="test/csv")
    response[
        "Content-Disposition"
    ] = f"attachment; filename={model_metadata.verbose_name}.csv"
    writer = csv.writer(response)
    fields = [
        field
        for field in model_metadata.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]
    writer.writerow([field.verbose_name for field in fields])
    for obj in queryset:
        row_data = []
        for field in fields:
            value = getattr(obj, field.name)
            row_data.append(value)
        writer.writerow(row_data)
    return response


def invoice_pdf(model: Order):
    url = reverse("orders:staff_order_pdf", args=[model.id])  # type: ignore
    return mark_safe(f'<a href="{url}" target="_blank">PDF</a>')


class OrderItemInline(admin.TabularInline):
    model = OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "first_name",
        "last_name",
        "email",
        "address",
        "postal_code",
        "city",
        "paid",
        "stripe_payment_intent",
        "created",
        "updated",
        invoice_pdf,
    ]
    list_filter = ["paid", "created", "updated"]
    inlines = [OrderItemInline]
    actions = [export_to_csv]
