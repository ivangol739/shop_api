from django.contrib import admin
from .models import (
    Shop, Category, Product, ProductInfo,
    Parameter, ProductParameter,
    Order, OrderItem,
    Contact, DeliveryAddress
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ['product', 'shop']

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Shop._meta.fields]
    search_fields = ['name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Category._meta.fields]
    filter_horizontal = ['shops']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Product._meta.fields]
    search_fields = ['name']
    list_filter = ['category']
    autocomplete_fields = ['category']

@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductInfo._meta.fields]
    search_fields = ['name']
    list_filter = ['product']
    autocomplete_fields = ['product', 'shop']

@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Parameter._meta.fields]
    search_fields = ['name']

@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductParameter._meta.fields]
    autocomplete_fields = ['product_info', 'parameter']
    search_fields = ['value']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.fields]
    list_filter = ['status']
    search_fields = ['user__username']
    autocomplete_fields = ['user']
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OrderItem._meta.fields]
    list_filter = ['shop', 'product']
    autocomplete_fields = ['order', 'product', 'shop']
    search_fields = ['product__name']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Contact._meta.fields]
    search_fields = ['last_name', 'first_name', 'email']
    autocomplete_fields = ['user']

@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DeliveryAddress._meta.fields]
    search_fields = ['address_line', 'city', 'country']
    autocomplete_fields = ['user']