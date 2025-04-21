import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from backend.models import Product, Category, ProductInfo, Shop, Order, OrderItem, Contact, DeliveryAddress
from rest_framework import status
from unittest.mock import patch
from time import sleep

User = get_user_model()

# Фикстура для регистрации пользователя и получения токена
@pytest.fixture
def auth_token(client):
    user_data = {
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "strongpassword123"
    }
    # Регистрируем пользователя
    register_url = reverse('backend:register')
    response = client.post(register_url, user_data, format='json')

    # Получаем токен
    token = response.data['token']
    return token

@pytest.mark.django_db
def test_register_user(client):
    url = reverse("backend:register")
    data = {
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "strongpassword123"
    }
    response = client.post(url, data, format='json')
    assert response.status_code == 201
    assert 'token' in response.data
    assert response.data['user']['username'] == "testuser"

@pytest.mark.django_db
def test_login_user(client):
    user = User.objects.create_user(
        username="testuser",
        password="strongpassword123",
        email="test@example.com"
    )
    client = APIClient()
    url = reverse("backend:login")
    data = {
        "username": "testuser",
        "password": "strongpassword123"
    }

    response = client.post(url, data, format='json')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert 'token' in response.data
    assert 'user' in response.data
    assert response.data['user']['username'] == "testuser"

@pytest.mark.django_db
def test_product_list_view(client, auth_token):
    category = Category.objects.create(name='Test Category')
    Product.objects.create(name='Product 1', category=category)
    Product.objects.create(name='Product 2', category=category)
    client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + auth_token
    url = reverse('backend:products')
    response = client.get(url)

    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    assert response.data[0]['name'] == 'Product 1'
    assert response.data[0]['category'] == 'Test Category'

@pytest.mark.django_db
def test_product_detail_view_success(client, auth_token):
    category = Category.objects.create(name="Test Category")
    product = Product.objects.create(name="Test Product", category=category)
    shop = Shop.objects.create(name="Test Shop")
    product_info = ProductInfo.objects.create(
        product=product,
        shop=shop,
        name="Test Product Info",
        quantity=10,
        price=100.00,
        price_rrc=120.00,
    )

    url = reverse('backend:product', kwargs={'product_id': product.id})
    client.defaults['HTTP_AUTHORIZATION'] = f'Token {auth_token}'

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert 'name' in response.data
    assert response.data['name'] == product_info.name
    assert float(response.data['price']) == product_info.price

@pytest.mark.django_db
def test_product_detail_view_not_found(client, auth_token):
    non_existing_product_id = 9999
    url = reverse('backend:product', kwargs={'product_id': non_existing_product_id})
    client.defaults['HTTP_AUTHORIZATION'] = f'Token {auth_token}'  # исправлено с Bearer

    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data == {'error': 'Product not found'}


@pytest.mark.django_db
def test_cart_delete_view(client, auth_token):
    client.defaults['HTTP_AUTHORIZATION'] = f'Token {auth_token}'

    category = Category.objects.create(name="Test Category")
    product = Product.objects.create(name="Test Product", category=category)
    shop = Shop.objects.create(name="Test Shop")
    product_info = ProductInfo.objects.create(
        product=product,
        shop=shop,
        name="Test Info",
        quantity=20,
        price=100.0,
        price_rrc=120.0,
    )
    user = User.objects.get(username='testuser')
    order = Order.objects.create(user=user, status="cart")
    order_item = OrderItem.objects.create(order=order, product=product, shop=shop, quantity=1)

    url = reverse('backend:cart-delete', kwargs={'item_id': order_item.id})
    response = client.delete(url)

    assert response.status_code == 204


@pytest.mark.django_db
def test_cart_add_view(client, auth_token):
    client.defaults['HTTP_AUTHORIZATION'] = f'Token {auth_token}'

    category = Category.objects.create(name="Test Category")
    product = Product.objects.create(name="Test Product", category=category)
    shop = Shop.objects.create(name="Test Shop")
    product_info = ProductInfo.objects.create(
        product=product,
        shop=shop,
        name="Test Product Info",
        quantity=20,
        price=100.0,
        price_rrc=120.0,
    )

    url = reverse('backend:cart-add')
    data = {
        "product_id": product_info.id,
        "quantity": 3
    }
    response = client.post(url, data, format='json')

    assert response.status_code == 201
    assert response.data['quantity'] == 3
    assert response.data['product_id'] == product.id

@pytest.mark.django_db
@patch("backend.views.send_email_task.delay")
def test_order_confirm_view(mock_send_email, client, auth_token):
    client.defaults['HTTP_AUTHORIZATION'] = f'Token {auth_token}'
    user = User.objects.get(username='testuser')

    order = Order.objects.create(user=user, status='cart')
    contact = Contact.objects.create(
        user=user, first_name='Иван', last_name='Иванов',
        phone='1234567890', email='ivan@example.com'
    )
    address = DeliveryAddress.objects.create(
        user=user, address_line='ул. Ленина, 1', city='Москва', country='Россия'
    )

    url = reverse('backend:order-confirm')
    data = {
        "contact_id": contact.id,
        "delivery_address": address.id
    }

    response = client.post(url, data, format='json')

    assert response.status_code == 200
    assert response.data['message'] == 'Заказ подтверждён и email отправлен'

    order.refresh_from_db()
    assert order.status == 'confirmed'

    mock_send_email.assert_called_once()

