from celery import shared_task
from PIL import Image
import os
from django.core.files.storage import default_storage
import time

@shared_task
def image_shop_data_task(file_path):
    from .utils.import_data import import_shop_data
    import_shop_data(file_path)


@shared_task
def send_email_task(subject, message, from_email, recipient_list):
    from django.core.mail import send_mail
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)


@shared_task
def resize_image_task(image_path, width, height, old_image_path=None):
    """
    Уменьшает размер изображения до заданных размеров (width x height).
    :param image_path: Путь к загруженному изображению
    :param width: Ширина (300px)
    :param height: Высота (300px)
    :param old_image_path: Путь к старому изображению для удаления
    """
    try:
        time.sleep(30)  # задержка на 30 секунд для теста
        with default_storage.open(image_path, 'rb') as f:
            img = Image.open(f)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            img.save(image_path, img.format)

        if old_image_path and os.path.exists(old_image_path) and old_image_path != image_path:
                    default_storage.delete(old_image_path)

    except Exception as e:
        print(f"Ошибка при обработке изображения: {e}")