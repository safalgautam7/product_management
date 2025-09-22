from django.db.models import Max
from rest_framework.views import APIView
from .serializers import *
from api.models import Product,Order, OrderItem
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView



class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.exclude(stock__gt=0)
    serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'product_id'

    
class OrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related(
        'items','items__product',
        ).all()
    serializer_class = OrderSerializer
    
    
class UserOrderListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.prefetch_related(
        'items','items__product',
        ).all()
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        return qs.filter(user=user)
    
    
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