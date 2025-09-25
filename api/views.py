from django.db.models import Max
from rest_framework.views import APIView
from .serializers import *
from api.models import Product,Order, OrderItem
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny,
)
from rest_framework.views import APIView
from rest_framework import viewsets
from api.filters import ProductFilter,InStockFilterBackend
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination,LimitOffsetPagination


class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.order_by('pk')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends=[
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend,
        ]
    search_fields = ['=name','description']
    ordering_fields = ['name','price','stock']
    
    # pagination_class= PageNumberPagination
    # pagination_class.page_size=2
    # pagination_class.page_query_param='pagenum'
    # pagination_class.page_size_query_param='size'
    # pagination_class.max_page_size=6
    
    pagination_class=LimitOffsetPagination
    
    
    def get_permissions(self):
        self.permission_classes= [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'product_id'
    
    
    def get_permissions(self):
        self.permission_classes= [AllowAny]
        if self.request.method in ['PUT','PATCH','DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product').all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    
# class OrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related(
#         'items','items__product',
#         ).all()
#     serializer_class = OrderSerializer
    
    
# class UserOrderListAPIView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = Order.objects.prefetch_related(
#         'items','items__product',
#         ).all()
#     serializer_class = OrderSerializer
    
#     def get_queryset(self):
#         user = self.request.user
#         qs = super().get_queryset()
#         return qs.filter(user=user)
    
    
class ProductInfoAPIView(APIView):
    def get(self,request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products':products,
            'count': len(products),
            'max_price': products.aggregate(max_price = Max('price'))['max_price']
        })
        return Response(serializer.data)
        
# @api_view(['GET'])
# def product_info(request):
#     products = Product.objects.all()
#     serializer = ProductInfoSerializer({
#         'products':products,
#         'count': len(products),
#         'max_price': products.aggregate(max_price = Max('price'))['max_price']
#     })
#     return Response(serializer.data)