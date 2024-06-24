from http import HTTPStatus
from django.http import HttpRequest
from rest_framework import generics, viewsets
from rest_framework.response import Response as RestResponse
import rest_framework.decorators as RestDecorators
from api.pagination import StardardResultsSetPagination
from api.serializers import CategorySerializer, ProductSerializer
from shop.models import Category, Product
from rest_framework.settings import api_settings


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("slug")
    serializer_class = ProductSerializer
    pagination_class = StardardResultsSetPagination


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("slug")
    serializer_class = CategorySerializer

    @RestDecorators.action(
        detail=False,
        methods=["get"],
        authentication_classes=[],
        permission_classes=[],
    )
    def count(self, request: HttpRequest, *args, **kwargs):
        count = self.queryset.count()
        return RestResponse(
            {
                "number_of_categories": count,
                "signature": "Lee",
                "path": request.get_full_path(),
            }
        )

    def destroy(self, request: HttpRequest, *args, **kwargs):
        return RestResponse(
            {"error": "unsupported operation", "url": request.get_full_path()},
            HTTPStatus.BAD_REQUEST,
        )
