import yaml
from django.db import transaction
from ..models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


def load_data_from_yaml(file_path):
    """
    Загружает данные из YAML файла и возвращает их в виде словаря
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


@transaction.atomic
def import_shop_data(file_path):
    """
    Загружает данные из YAML файла и сохраняет их в базе данных
    """
    data = load_data_from_yaml(file_path)  # Используем переданный параметр

    # Создание или получение магазина
    shop, _ = Shop.objects.get_or_create(
        name=data['shop'],
        defaults={'url': f'https://{data["shop"].lower()}.ru'}
    )

    # Обработка категорий
    category_map = {}
    for category_data in data['categories']:
        category, _ = Category.objects.get_or_create(
            id=category_data['id'],
            defaults={
                'name': category_data['name'],
            })
        category.shops.add(shop)
        category_map[category_data['id']] = category

    # Обработка товаров
    for good in data['goods']:
        # Создание продукта
        product, _ = Product.objects.get_or_create(
            name=good['name'],
            defaults={
                'category': category_map[good['category']],
            }
        )

        # Создание информации о продукте
        product_info, _ = ProductInfo.objects.get_or_create(
            product=product,
            shop=shop,
            defaults={
                'name': good['name'],
                'quantity': good['quantity'],
                'price': good['price'],
                'price_rrc': good['price_rrc'],
            }
        )

        # Обработка параметров продукта
        for param_name, param_value in good['parameters'].items():
            parameter, _ = Parameter.objects.get_or_create(name=param_name)
            ProductParameter.objects.get_or_create(
                product_info=product_info,
                parameter=parameter,
                value=str(param_value)
            )
    print(f"Успешно импортированы данные для магазина {shop.name}")