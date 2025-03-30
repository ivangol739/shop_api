from itertools import product

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

    def get_category(self, obj):
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

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'dt', 'status', 'items']

class OrderDetailSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name', read_only=True)
    shop = serializers.CharField(source='shop.name', read_only=True)
    price = serializers.DecimalField(source='get_product_info_price', max_digits=2, decimal_places=2, read_only=True)
    quantity = serializers.IntegerField()
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = OrderItem
        fields = ["product", "shop", "price", "quantity", "total_price"]

    def get_product_info_price(self, obj):
        product_info = ProductInfo.objects.filter(product=obj.product, shop=obj.shop).first()
        return product_info.price if product_info else None

    def get_total_price(self, obj):
        product_info = ProductInfo.objects.filter(product=obj.product, shop=obj.shop).first()
        return product_info.price * obj.quantity


class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = ['id', 'user', 'address_line', 'city', 'postal_code', 'country']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'type', 'user', 'value']
