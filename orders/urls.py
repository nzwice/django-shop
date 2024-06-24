from django.urls import path

from orders import views


app_name = "orders"

urlpatterns = [
    path("create/", views.order_create, name="order_create"),
    path(
        "staff/order/<int:order_id>/pdf",
        views.staff_order_pdf,
        name="staff_order_pdf",
    ),
]
