from itertools import product
from operator import ifloordiv

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import password_changed
from rest_framework import serializers
from .models import Product, ProductInfo, Order, OrderItem, DeliveryAddress, Contact


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'name', 'category']

    def get_category(self, obj) -> str:
        return obj.category.name

class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = ProductInfo
        fields = ['id', 'product', 'shop', 'name', 'quantity', 'price', 'price_rrc']

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=ProductInfo.objects.all(), source='product')
    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'quantity']

class OrderConfirmSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(required=True)
    contact_id = serializers.IntegerField(required=True)
    delivery_address = serializers.IntegerField(required=True)
    class Meta:
        model = Order
        fields = ['order_id', 'contact_id', 'delivery_address']

class OrderDetailSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name', read_only=True)
    shop = serializers.CharField(source='shop.name', read_only=True)
    price = serializers.SerializerMethodField()
    quantity = serializers.IntegerField()
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = OrderItem
        fields = ["product", "shop", "price", "quantity", "total_price"]

    def get_price(self, obj) -> float:
        product_info = ProductInfo.objects.filter(product=obj.product, shop=obj.shop).first()
        return product_info.price if product_info else None

    def get_total_price(self, obj) -> float:
        product_info = ProductInfo.objects.filter(product=obj.product, shop=obj.shop).first()
        return (product_info.price * obj.quantity) if product_info else 0

class CartSerializer(serializers.ModelSerializer):
    items = OrderDetailSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['items', 'total_cart_price']

    def get_total_cart_price(self, obj) -> float:
        total = 0
        for item in obj.items.all():
            product_info = ProductInfo.objects.filter(product=item.product, shop=item.shop).first()
            total += (product_info.price if product_info else 0) * item.quantity
        return total

class OrderHistorySerializer(serializers.ModelSerializer):
    total_order_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'dt', 'status', 'total_order_price']

    def get_total_order_price(self, obj) -> float:
        total = 0
        for item in obj.items.all():
            product_info = ProductInfo.objects.filter(product=item.product, shop=item.shop).first()
            total += (product_info.price if product_info else 0) * item.quantity
        return total

class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = ['id', 'address_line', 'city', 'postal_code', 'country']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'last_name', 'first_name', 'middle_name', 'email', 'phone']

