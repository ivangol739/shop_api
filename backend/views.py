import requests
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model
from .models import Product, ProductInfo, Order, OrderItem, DeliveryAddress, Contact, UserProfile
from .serializers import (
    UserRegisterSerializer, UserLoginSerializer, ProductSerializer, ProductInfoSerializer, ContactSerializer,
    OrderItemSerializer, DeliveryAddressSerializer, OrderConfirmSerializer,
    CartSerializer, OrderHistorySerializer, OrderFullDetailSerializer, OrderStatusUpdateSerializer, UserAvatarSerializer,
    ProductImageSerializer
)
from .tasks import send_email_task, resize_image_task

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    @extend_schema(
        request=UserRegisterSerializer,
        responses={201: UserRegisterSerializer},
        summary="Register a new user",
        description="Register a new user with the provided username, email, and password.",
        tags=['Authentication'],
    )

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.create(user=user)
            try:
                send_email_task.delay(
                    subject="Подтверждение регистрации",
                    message=f"Здравствуйте, {user.username}!\n\nВаш аккаунт успешно создан.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )
            except Exception as e:
                print(f"Ошибка отправки email: {e}")

            return Response({
                'token': token.key,
                'user': UserRegisterSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    @extend_schema(
        request=UserLoginSerializer,
        responses={200: UserLoginSerializer},
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
                'user': UserLoginSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class GoogleOAuthCallbackAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            return Response({"error": "Missing code"}, status=400)

        # Меняем code на access_token и id_token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            "client_secret": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            "redirect_uri": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI,
            "grant_type": "authorization_code"
        }

        token_response = requests.post(token_url, data=data)
        if token_response.status_code != 200:
            return Response({"error": "Failed to fetch tokens from Google"}, status=400)

        tokens = token_response.json()
        id_token = tokens.get("id_token")

        # Проверяем id_token и получаем инфо
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests

        try:
            idinfo = google_id_token.verify_oauth2_token(
                id_token,
                google_requests.Request(),
                settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
            )
            email = idinfo.get("email")
            first_name = idinfo.get("given_name", "")
            last_name = idinfo.get("family_name", "")
            username = email.split("@")[0]

            user, created = User.objects.get_or_create(email=email, defaults={
                "username": username,
                "first_name": first_name,
                "last_name": last_name
            })

            if created:
                user.set_unusable_password()
                user.save()

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
            })

        except Exception as e:
            return Response({"error": "Token verification failed", "details": str(e)}, status=400)

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
        print(products)
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
        except ProductInfo.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @extend_schema(
        responses={200: CartSerializer},
        summary="List all items in the cart",
        description="List all items in the shopping cart.",
        tags=['Cart'],
    )

    def get(self, request):
        order = Order.objects.filter(user=request.user, status='cart').first()
        if not order:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_200_OK)
        serializer = CartSerializer(order)
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


class ContactView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: ContactSerializer(many=True)},
        summary="List all contacts",
        description="List all contacts.",
        tags=['Contact'],
    )

    def get(self, request):
        contacts = Contact.objects.filter(user=request.user)
        if not contacts:
            return Response({'error': 'No contacts found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)


class ContactAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ContactSerializer,
        responses={201: ContactSerializer},
        summary="Adding a contact",
        description="Adding a contact.",
        tags=['Contact'],
    )

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={204: None},
        summary="Delete a contact",
        description="Deletes a specific contact by its ID.",
        tags=['Contact'],
    )

    def delete(self, request, contact_id):
        contact = get_object_or_404(Contact, id=contact_id, user=request.user)
        contact.delete()
        return Response({'message': "Contact deleted"}, status=status.HTTP_204_NO_CONTENT)


class OrderConfirmView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=OrderConfirmSerializer,
        responses={200: None},
        summary="Confirm an order",
        description="Confirm an order.",
        tags=['Order'],
    )

    def post(self, request):
        serializer = OrderConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        contact_id = serializer.validated_data["contact_id"]
        delivery_address_id = serializer.validated_data["delivery_address"]

        order = get_object_or_404(Order, user=request.user, status='cart')
        contact = get_object_or_404(Contact, id=contact_id, user=request.user)
        delivery_address = get_object_or_404(DeliveryAddress, id=delivery_address_id, user=request.user)
        order.status = 'confirmed'
        order.save()
        try:
            send_email_task.delay(
                "Подтверждение заказа!",
                f"Ваш заказ #{order.id} подтверждён.\n"
                f"Контактное лицо: {contact.first_name} {contact.last_name}, Телефон: {contact.phone}, Email: {contact.email}\n"
                f"Адрес доставки: {delivery_address.address_line}, {delivery_address.city}, {delivery_address.country}",
                "shop@example.com",
                [request.user.email],
            )
        except Exception as e:
            print(f"Ошибка отправки email: {e}")

        return Response({'message': 'Заказ подтверждён и email отправлен'}, status=status.HTTP_200_OK)


class OrderHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: OrderHistorySerializer(many=True)},
        summary="List all orders",
        description="Getting a list of all user's orders with their status, date, and total amount.",
        tags=['Order'],
    )

    def get(self, request):
        orders = Order.objects.filter(user=request.user).exclude(status='cart').order_by('-dt')
        if not orders:
            return Response({'error': 'No orders found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderHistorySerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: OrderFullDetailSerializer},
        summary="Get order details",
        description="Getting details of a specific order by its ID.",
        tags=['Order'],
    )

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user, status='confirmed')
            serializer = OrderFullDetailSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=OrderStatusUpdateSerializer,
        responses={200: None},
        summary="Update order status",
        description="Updating the status of an order.",
        tags=['Order'],
    )

    def patch(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order_old = order.status
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"old_status": order_old, "new_status": order.status}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAvatarView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=UserAvatarSerializer,
        responses={200: UserAvatarSerializer},
        summary="Upload user avatar",
        description="Upload the avatar of a user.",
        tags=['UserAvatar'],
    )

    def post(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserAvatarSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            old_avatar = profile.avatar.path if profile.avatar else None
            serializer.save()

            resize_image_task.delay(profile.avatar.path, 300, 300, old_avatar)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ProductImageSerializer,
        responses={200: ProductImageSerializer},
        summary="Upload product image",
        description="Upload an image for a product.",
        tags=['Products'],
    )

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        serializer = ProductImageSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            old_image = product.image.path if product.image else None
            serializer.save()
            resize_image_task.delay(product.image.path, 300, 300, old_image)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




