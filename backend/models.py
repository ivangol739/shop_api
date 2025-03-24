from django.db import models
from django.contrib.auth.models import User


class Shop(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return self.name


class Category(models.Model):
    shops = models.ManyToManyField(Shop, related_name='categories')
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_infos')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='product_infos')
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_rrc = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информация о продуктах'

    def __str__(self):
        return f"{self.name} ({self.shop})"


class Parameter(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='product_parameters')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name='product_parameters')
    value = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Параметр продукта'
        verbose_name_plural = 'Параметры продуктов'

    def __str__(self):
        return f"{self.parameter}: {self.value}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Заказ {self.id} от {self.dt}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f"{self.product} x{self.quantity}"

class Contact(models.Model):
    type = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    value = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f"{self.type}: {self.value}"

class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_addresses')
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставки'

    def __str__(self):
        return f"{self.address_line}, {self.city}, {self.country}"  