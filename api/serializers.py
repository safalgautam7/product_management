from django.db import transaction
from rest_framework import serializers 
from .models import Product,Order,OrderItem
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'is_staff',
            'is_superuser',
            'orders',
        )


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'stock',
        ]
        
    def validate_price(self,value):
        if value <=0:
            raise serializers.ValidationError("Price must be greather than 0.")
        return value
    

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source = 'product.name')
    product_price = serializers.DecimalField(source = 'product.price',max_digits=10,
    decimal_places=2
    )
    class Meta:
        model = OrderItem
        fields = (
            'product_name',
            'product_price',
            'quantity',
            'item_subtotal'
            )
        
        
class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = ('product','quantity')
            
    order_id = serializers.UUIDField(read_only=True)
    items = OrderItemCreateSerializer(many = True,required = False)
    
    def create(self,validated_data):
        orderitem_data = validated_data.pop('items')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            
            for item in orderitem_data:
                OrderItem.objects.create(order=order,**item)
                
            return order
    
    def update(self, instance, validated_data):
        orderitem_data = validated_data.pop('items')
        
        
        with transaction.atomic():
        #this updates the order but not the nested order items
            instance = super().update(instance,validated_data)
            
            if orderitem_data is not None:
                #Clear existing items (optional, depends on requirements)
                instance.items.all().delete()
                
                #Recreate items with the updated data
                for item in orderitem_data:
                    OrderItem.objects.create(order=instance, **item)
        return instance

            
        
    class Meta:
        model = Order
        fields = (
                  'order_id',
                  'user',
                  'status',
                  'items',
        )
        extra_kwargs = {
            'user':{'read_only':True}
        }
        
        
class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(read_only=True)
    # user = serializers.SlugRelatedField(
    #     queryset = User.objects.all(),
    #     slug_field = 'username'
    # )
    #read_only = True ensures that it is not required when making an order
    items = OrderItemSerializer(many = True, read_only = True)
    total_price = serializers.SerializerMethodField(method_name = 'get_total_price')
    
    def get_total_price(self,obj):
        order_items = obj.items.all()
        return sum(order_item.item_subtotal for order_item in order_items)
    
        
    class Meta:
        model = Order
        fields = ('order_id', 'created_at', 'user', 'status', 'items','total_price',)
        

class ProductInfoSerializer(serializers.Serializer):
    #get all products, count of products, max price
    products = ProductSerializer(many = True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()