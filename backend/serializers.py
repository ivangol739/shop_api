from django.contrib.auth.models import User
from django.contrib.auth.password_validation import password_changed
from rest_framework import serializers
from .models import Product, ProductInfo, Order, OrderItem, DeliveryAddress, Contact


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='get_category', read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'category']

class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    shop = serializers.CharField(source='shop.name', read_only=True)
    class Meta:
        model = ProductInfo
        fields = ['id', 'product', 'shop', 'name', 'quantity', 'price', 'price_rrc']

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=ProductInfo.objects.all(), source='product')
    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'quantity']

class OrderConfirmSerializer(serializers.ModelSerializer):
    contact_id = serializers.IntegerField(required=True)
    delivery_address = serializers.IntegerField(required=True)
    class Meta:
        model = Order
        fields = ['contact_id', 'delivery_address']

class OrderDetailSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name', read_only=True)
    shop = serializers.CharField(source='shop.name', read_only=True)
    price = serializers.FloatField(source='get_price', read_only=True)
    quantity = serializers.IntegerField()
    total_price = serializers.FloatField(source='get_total_price', read_only=True)
    class Meta:
        model = OrderItem
        fields = ["id", "product", "shop", "price", "quantity", "total_price"]

class CartSerializer(serializers.ModelSerializer):
    items = OrderDetailSerializer(many=True, read_only=True)
    total_cart_price = serializers.FloatField(source='get_total_order_price', read_only=True)
    class Meta:
        model = Order
        fields = ['items', 'total_cart_price']

class OrderHistorySerializer(serializers.ModelSerializer):
    total_order_price = serializers.FloatField(source='get_total_order_price', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'dt', 'status', 'total_order_price']

class OrderFullDetailSerializer(serializers.ModelSerializer):
    items = OrderDetailSerializer(many=True, read_only=True)
    total_order_price = serializers.FloatField(source='get_total_order_price', read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'dt', 'items', 'total_order_price']

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
        extra_kwargs = {'status': {'required': True}}

class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = ['id', 'address_line', 'city', 'postal_code', 'country']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'last_name', 'first_name', 'middle_name', 'email', 'phone']

