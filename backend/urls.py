from django.urls import path
from backend.views import RegisterView, LoginView, ProductListView, ProductDetailView

app_name = "backend"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("products/", ProductListView.as_view(), name="products"),
    path("products/<int:product_id>/", ProductDetailView.as_view(), name="product"),
]