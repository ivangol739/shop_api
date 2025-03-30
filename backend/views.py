from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from drf_spectacular.utils import extend_schema
from .models import Product, ProductInfo, Order, OrderItem, DeliveryAddress
from .serializers import (
    UserSerializer, ProductSerializer, ProductInfoSerializer,
    OrderSerializer, OrderItemSerializer, DeliveryAddressSerializer, OrderDetailSerializer
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    @extend_schema(
        request=UserSerializer,
        responses={201: UserSerializer},
        summary="Register a new user",
        description="Register a new user with the provided username, email, and password.",
        tags=['Authentication'],
    )

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer},
        summary="Login a user",
        description="Login a user with the provided username and password.",
        tags=['Authentication'],
    )

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ProductListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @extend_schema(
        responses={200: ProductSerializer(many=True)},
        summary="List all products",
        description="List all available products.",
        tags=['Products'],
    )

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @extend_schema(
        responses={200: ProductInfoSerializer},
        summary="Retrieve a product",
        description="Retrieve details of a specific product.",
        tags=['Products'],
    )

    def get(self, request, product_id):
        try:
            product_info = ProductInfo.objects.get(product_id=product_id)
            serializer = ProductInfoSerializer(product_info)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @extend_schema(
        responses={200: OrderDetailSerializer(many=True)},
        summary="List all items in the cart",
        description="List all items in the shopping cart.",
        tags=['Cart'],
    )

    def get(self, request):
        order = Order.objects.filter(user=request.user, status='cart').first()
        if not order:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_200_OK)
        order_items = OrderItem.objects.filter(order=order)
        serializer = OrderDetailSerializer(order_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=OrderItemSerializer,
        responses={201: OrderItemSerializer},
        summary="Adding an item to the cart",
        description="Adding an item to the cart.",
        tags=['Cart'],
    )

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        product_info = get_object_or_404(ProductInfo, id=product_id)
        order, _ = Order.objects.get_or_create(user=request.user, status="cart")
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product=product_info.product,
            shop=product_info.shop,
            defaults={'quantity': quantity}
        )
        if not created:
            order_item.quantity += quantity
            order_item.save()
        else:
            order_item.quantity = quantity
        order_item.save()
        serializer = OrderItemSerializer(order_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CartDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={204: None},
        summary="Clear the cart",
        description="Deletes a specific product from the shopping cart by its ID.",
        tags=['Cart'],
    )

    def delete(self, request, item_id):
        order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__status='cart')
        order_item.delete()
        return Response({'message': "Item deleted"}, status=status.HTTP_204_NO_CONTENT)


class DeliveryAddressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: DeliveryAddressSerializer(many=True)},
        summary="List all delivery addresses",
        description="List all delivery addresses.",
        tags=['Delivery Address'],
    )

    def get(self, request):
        addresses = DeliveryAddress.objects.filter(user=request.user)
        if not addresses:
            return Response({'error': 'No addresses found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = DeliveryAddressSerializer(addresses, many=True)
        return Response(serializer.data)

class DeliveryAddressAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=DeliveryAddressSerializer,
        responses={201: DeliveryAddressSerializer},
        summary="Adding a delivery address",
        description="Adding a delivery address.",
        tags=['Delivery Address'],
    )

    def post(self, request):
        serializer = DeliveryAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeliveryAddressDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={204: None},
        summary="Delete a delivery address",
        description="Deletes a specific delivery address by its ID.",
        tags=['Delivery Address'],
    )

    def delete(self, request, address_id):
        address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
        address.delete()
        return Response({'message': "Address deleted"}, status=status.HTTP_204_NO_CONTENT)