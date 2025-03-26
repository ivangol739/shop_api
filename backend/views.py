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
    OrderSerializer, OrderItemSerializer, DeliveryAddressSerializer
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


