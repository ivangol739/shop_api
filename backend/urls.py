from django.urls import path
from backend.views import (RegisterView, LoginView, ProductListView, ProductDetailView, CartAddView,
                           CartDeleteView, CartView, DeliveryAddressAddView, DeliveryAddressDeleteView,
                           DeliveryAddressView,
                           ContactView, OrderConfirmView, OrderHistoryView, OrderDetailView, OrderStatusUpdateView)

app_name = "backend"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("products/", ProductListView.as_view(), name="products"),
    path("products/<int:product_id>/", ProductDetailView.as_view(), name="product"),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/add/", CartAddView.as_view(), name="cart-add"),
    path("cart/remove/<int:item_id>/", CartDeleteView.as_view(), name="cart-delete"),
    path("delivery-address/", DeliveryAddressView.as_view(), name="delivery-address"),
    path("delivery-address/add/", DeliveryAddressAddView.as_view(), name="delivery-address-add"),
    path("delivery-address/remove/<int:address_id>/", DeliveryAddressDeleteView.as_view(), name="delivery-address-delete"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("order-confirm/", OrderConfirmView.as_view(), name="order-confirm"),
    path("order/history/", OrderHistoryView.as_view(), name="order-history"),
    path("order/detail/<int:order_id>/", OrderDetailView.as_view(), name="order-detail"),
    path("order/<int:order_id>/status/", OrderStatusUpdateView.as_view(), name="order-detail"),
]