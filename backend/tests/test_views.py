import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_register_user():
    client = APIClient()
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