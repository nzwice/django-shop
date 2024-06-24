from django.urls import path
from api import views
from rest_framework import routers as rest_routers
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView


app_name = "api"

router = rest_routers.SimpleRouter()
router.register("categories", views.CategoryViewSet)

urlpatterns = [
    path("products/", views.ProductListView.as_view(), name="api_product_list"),
    path(
        "products/<int:pk>/",
        views.ProductDetailView.as_view(),
        name="api_product_detail",
    ),
    path("swagger/", SpectacularJSONAPIView.as_view(), name="swagger"),
    path(
        "swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="api:swagger"),
        name="api_swagger_ui",
    ),
]

urlpatterns += router.urls
